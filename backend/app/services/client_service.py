"""
שירות לקוחות: כל הלוגיקה שמתקשרת עם טבלת clients ב-Supabase.
"""
from typing import Optional
from datetime import datetime, timezone
from fastapi import HTTPException
from app.core.supabase_client import get_supabase_admin
from app.schemas.client import ClientCreate, ClientUpdate

TABLE = "clients"


class ClientService:
    def __init__(self):
        self.db = get_supabase_admin()

    def list_clients(self, search: Optional[str] = None, active_only: bool = True) -> list[dict]:
        query = self.db.table(TABLE).select("*")
        if active_only:
            query = query.eq("is_active", True)
        if search:
            query = query.or_(f"full_name.ilike.%{search}%,phone.ilike.%{search}%")
        result = query.order("full_name").execute()
        return result.data

    def get_client(self, client_id: str) -> Optional[dict]:
        result = self.db.table(TABLE).select("*").eq("id", client_id).maybe_single().execute()
        return result.data if result else None

    def create_client(self, payload: ClientCreate) -> dict:
        data = payload.model_dump(exclude_none=True, mode="json")
        result = self.db.table(TABLE).insert(data).execute()
        return result.data[0]

    def update_client(self, client_id: str, payload: ClientUpdate) -> Optional[dict]:
        data = payload.model_dump(exclude_unset=True, mode="json")
        if not data:
            return self.get_client(client_id)
        result = self.db.table(TABLE).update(data).eq("id", client_id).execute()
        return result.data[0] if result.data else None

    def delete_client(self, client_id: str, force: bool = False) -> bool:
        """מחיקה רכה. אם force=False, בודק תורים עתידיים פתוחים ומוחא מחאה."""
        if not force:
            now = datetime.now(timezone.utc)
            future_appts = (
                self.db.table("appointments")
                .select("id")
                .eq("client_id", client_id)
                .neq("status", "cancelled")
                .gt("start_time", now.isoformat())
                .execute()
            )
            if future_appts.data:
                count = len(future_appts.data)
                plural = count > 1
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"ללקוחה יש {count} תור{'ים' if plural else ''} עתידי{'ים' if plural else ''} "
                        f"פתוח{'ים' if plural else ''}. "
                        "בטלי אותם קודם, או הוסיפי force=true כדי למחוק בכל זאת."
                    ),
                )
        result = self.db.table(TABLE).update({"is_active": False}).eq("id", client_id).execute()
        return bool(result.data)
