"""
שירות תורים: ניהול היומן - יצירה, עדכון, שליפה לפי טווח תאריכים/לקוח.
"""
from typing import Optional
from datetime import datetime
from fastapi import HTTPException
from dateutil.parser import parse as parse_dt
from app.core.supabase_client import get_supabase_admin
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.services.google_calendar_service import GoogleCalendarService

TABLE = "appointments"


def _check_time_validity(start_time: datetime, end_time: datetime) -> None:
    if end_time <= start_time:
        raise HTTPException(status_code=400, detail="שעת הסיום חייבת להיות אחרי שעת ההתחלה")


class AppointmentService:
    def __init__(self):
        self.db = get_supabase_admin()
        self.gcal = GoogleCalendarService()

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _get_client_name(self, client_id: str) -> str:
        try:
            result = (
                self.db.table("clients")
                .select("full_name")
                .eq("id", client_id)
                .maybe_single()
                .execute()
            )
            return result.data["full_name"] if result.data else "לקוחה"
        except Exception:
            return "לקוחה"

    def _check_overlap(
        self, start_time: datetime, end_time: datetime, exclude_id: Optional[str] = None
    ) -> None:
        query = (
            self.db.table(TABLE)
            .select("id, start_time, client_id")
            .neq("status", "cancelled")
            .lt("start_time", end_time.isoformat())
            .gt("end_time", start_time.isoformat())
        )
        if exclude_id:
            query = query.neq("id", exclude_id)
        result = query.execute()
        if not result.data:
            return

        conflict = result.data[0]
        client_name = "לקוחה לא ידועה"
        try:
            cr = (
                self.db.table("clients")
                .select("full_name")
                .eq("id", conflict["client_id"])
                .maybe_single()
                .execute()
            )
            if cr.data:
                client_name = cr.data["full_name"]
        except Exception:
            pass

        try:
            fmt_start = parse_dt(conflict["start_time"]).strftime("%d/%m/%Y %H:%M")
        except Exception:
            fmt_start = conflict.get("start_time", "")

        raise HTTPException(
            status_code=409,
            detail=f"קיים תור חופף: {client_name} ב-{fmt_start}. יש לבטל אותו קודם.",
        )

    def _sync_create(self, appointment: dict) -> None:
        """מסנכרן תור חדש ל-Google Calendar (best-effort)."""
        if not self.gcal.enabled:
            return
        try:
            client_name = self._get_client_name(appointment["client_id"])
            event_id = self.gcal.create_event(appointment, client_name)
            if event_id:
                self.db.table(TABLE).update({"google_event_id": event_id}).eq("id", appointment["id"]).execute()
                appointment["google_event_id"] = event_id
        except Exception as exc:
            print(f"[Google Calendar] שגיאת סנכרון יצירה: {exc}")

    def _sync_update(self, appointment: dict) -> None:
        """מסנכרן עדכון ל-Google Calendar (best-effort)."""
        if not self.gcal.enabled:
            return
        try:
            event_id = appointment.get("google_event_id")
            if event_id:
                client_name = self._get_client_name(appointment["client_id"])
                self.gcal.update_event(event_id, appointment, client_name)
        except Exception as exc:
            print(f"[Google Calendar] שגיאת סנכרון עדכון: {exc}")

    def _sync_delete(self, appointment: dict) -> None:
        """מוחק אירוע מ-Google Calendar (best-effort)."""
        if not self.gcal.enabled:
            return
        try:
            event_id = appointment.get("google_event_id")
            if event_id:
                self.gcal.delete_event(event_id)
        except Exception as exc:
            print(f"[Google Calendar] שגיאת סנכרון מחיקה: {exc}")

    # ------------------------------------------------------------------ #
    # CRUD                                                                 #
    # ------------------------------------------------------------------ #

    def list_appointments(
        self,
        client_id: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> list[dict]:
        query = self.db.table(TABLE).select("*")
        if client_id:
            query = query.eq("client_id", client_id)
        if date_from:
            query = query.gte("start_time", date_from.isoformat())
        if date_to:
            query = query.lte("start_time", date_to.isoformat())
        result = query.order("start_time").execute()
        return result.data

    def get_appointment(self, appointment_id: str) -> Optional[dict]:
        result = self.db.table(TABLE).select("*").eq("id", appointment_id).maybe_single().execute()
        return result.data if result else None

    def create_appointment(self, payload: AppointmentCreate) -> dict:
        _check_time_validity(payload.start_time, payload.end_time)
        self._check_overlap(payload.start_time, payload.end_time)
        data = payload.model_dump(mode="json")
        result = self.db.table(TABLE).insert(data).execute()
        appointment = result.data[0]
        self._sync_create(appointment)
        return appointment

    def update_appointment(self, appointment_id: str, payload: AppointmentUpdate) -> Optional[dict]:
        data = payload.model_dump(exclude_unset=True, mode="json")
        if not data:
            return self.get_appointment(appointment_id)

        if "start_time" in data or "end_time" in data:
            existing = self.get_appointment(appointment_id)
            if not existing:
                return None
            new_start = parse_dt(data["start_time"]) if "start_time" in data else parse_dt(existing["start_time"])
            new_end = parse_dt(data["end_time"]) if "end_time" in data else parse_dt(existing["end_time"])
            _check_time_validity(new_start, new_end)
            self._check_overlap(new_start, new_end, exclude_id=appointment_id)

        result = self.db.table(TABLE).update(data).eq("id", appointment_id).execute()
        updated = result.data[0] if result.data else None
        if updated:
            self._sync_update(updated)
        return updated

    def delete_appointment(self, appointment_id: str) -> bool:
        existing = self.get_appointment(appointment_id)
        result = self.db.table(TABLE).delete().eq("id", appointment_id).execute()
        if result.data and existing:
            self._sync_delete(existing)
        return bool(result.data)
