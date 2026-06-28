"""
שירות תשלומים: רישום ושליפת תשלומים, כולל סיכום הכנסות פר לקוח.
"""
from typing import Optional
from fastapi import HTTPException
from app.core.supabase_client import get_supabase_admin
from app.schemas.payment import PaymentCreate, PaymentUpdate

TABLE = "payments"


class PaymentService:
    def __init__(self):
        self.db = get_supabase_admin()

    def list_payments(self, client_id: Optional[str] = None) -> list[dict]:
        query = self.db.table(TABLE).select("*")
        if client_id:
            query = query.eq("client_id", client_id)
        result = query.order("paid_at", desc=True).execute()
        return result.data

    def get_payment(self, payment_id: str) -> Optional[dict]:
        result = self.db.table(TABLE).select("*").eq("id", payment_id).maybe_single().execute()
        return result.data if result else None

    def create_payment(self, payload: PaymentCreate) -> dict:
        if payload.appointment_id:
            appt = (
                self.db.table("appointments")
                .select("id, client_id")
                .eq("id", payload.appointment_id)
                .maybe_single()
                .execute()
            )
            if not appt.data:
                raise HTTPException(status_code=400, detail="התור שצוין אינו קיים במערכת")
            if appt.data["client_id"] != payload.client_id:
                raise HTTPException(status_code=400, detail="התור שצוין אינו שייך ללקוחה זו")
        data = payload.model_dump(mode="json")
        result = self.db.table(TABLE).insert(data).execute()
        return result.data[0]

    def update_payment(self, payment_id: str, payload: PaymentUpdate) -> Optional[dict]:
        data = payload.model_dump(exclude_unset=True, mode="json")
        if not data:
            return self.get_payment(payment_id)
        result = self.db.table(TABLE).update(data).eq("id", payment_id).execute()
        return result.data[0] if result.data else None

    def delete_payment(self, payment_id: str) -> bool:
        result = self.db.table(TABLE).delete().eq("id", payment_id).execute()
        return bool(result.data)

    def get_client_total(self, client_id: str) -> float:
        result = self.db.table(TABLE).select("amount").eq("client_id", client_id).execute()
        return sum(row["amount"] for row in result.data)
