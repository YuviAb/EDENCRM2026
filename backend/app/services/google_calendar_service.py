"""
סנכרון תורים עם Google Calendar דרך Service Account.
אם GOOGLE_SERVICE_ACCOUNT_FILE או GOOGLE_CALENDAR_ID ריקים — השירות מושבת בשקט.
"""
from __future__ import annotations
from typing import Optional
from app.core.config import settings


def _to_iso(value) -> str:
    """מחזיר מחרוזת ISO — עובד גם על datetime וגם על str."""
    return value if isinstance(value, str) else value.isoformat()


class GoogleCalendarService:
    def __init__(self):
        self._service = None
        if settings.GOOGLE_SERVICE_ACCOUNT_FILE and settings.GOOGLE_CALENDAR_ID:
            try:
                from google.oauth2 import service_account
                from googleapiclient.discovery import build
                creds = service_account.Credentials.from_service_account_file(
                    settings.GOOGLE_SERVICE_ACCOUNT_FILE,
                    scopes=["https://www.googleapis.com/auth/calendar.events"],
                )
                self._service = build("calendar", "v3", credentials=creds, cache_discovery=False)
                print("[Google Calendar] חיבור הצליח ✓")
            except Exception as exc:
                print(f"[Google Calendar] לא ניתן להתחבר: {exc}")

    @property
    def enabled(self) -> bool:
        return self._service is not None

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def create_event(self, appointment: dict, client_name: str) -> Optional[str]:
        """מוסיף אירוע, מחזיר את event_id של Google."""
        if not self.enabled:
            return None
        event = self._build_event(appointment, client_name)
        result = (
            self._service.events()
            .insert(calendarId=settings.GOOGLE_CALENDAR_ID, body=event)
            .execute()
        )
        return result.get("id")

    def update_event(self, event_id: str, appointment: dict, client_name: str) -> None:
        """מעדכן אירוע קיים."""
        if not self.enabled or not event_id:
            return
        event = self._build_event(appointment, client_name)
        self._service.events().update(
            calendarId=settings.GOOGLE_CALENDAR_ID,
            eventId=event_id,
            body=event,
        ).execute()

    def delete_event(self, event_id: str) -> None:
        """מוחק אירוע. מתעלם מ-404 (כבר נמחק ידנית)."""
        if not self.enabled or not event_id:
            return
        try:
            self._service.events().delete(
                calendarId=settings.GOOGLE_CALENDAR_ID,
                eventId=event_id,
            ).execute()
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    # Private helpers                                                       #
    # ------------------------------------------------------------------ #

    def _build_event(self, appointment: dict, client_name: str) -> dict:
        notes = appointment.get("notes") or ""
        price = appointment.get("price")
        if price is not None:
            notes = f"₪{price}\n{notes}".strip()

        return {
            "summary": f"{client_name} — {appointment['treatment_name']}",
            "description": notes,
            "start": {"dateTime": _to_iso(appointment["start_time"]), "timeZone": "Asia/Jerusalem"},
            "end": {"dateTime": _to_iso(appointment["end_time"]), "timeZone": "Asia/Jerusalem"},
        }
