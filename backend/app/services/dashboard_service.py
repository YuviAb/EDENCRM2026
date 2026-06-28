"""
שירות דשבורד: מחשב סיכומים יומיים/חודשיים לתצוגת הדף הראשי.
"""
from datetime import datetime
from zoneinfo import ZoneInfo
from app.core.supabase_client import get_supabase_admin

TZ = ZoneInfo("Asia/Jerusalem")


class DashboardService:
    def __init__(self):
        self.db = get_supabase_admin()

    def get_today_summary(self) -> dict:
        now = datetime.now(TZ)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        appts_result = (
            self.db.table("appointments")
            .select("*, clients(full_name)")
            .gte("start_time", today_start.isoformat())
            .lte("start_time", today_end.isoformat())
            .order("start_time")
            .execute()
        )

        payments_result = (
            self.db.table("payments")
            .select("amount")
            .gte("paid_at", today_start.isoformat())
            .lte("paid_at", today_end.isoformat())
            .execute()
        )

        clients_result = (
            self.db.table("clients")
            .select("id")
            .eq("is_active", True)
            .gte("created_at", month_start.isoformat())
            .execute()
        )

        appointments = []
        for appt in (appts_result.data or []):
            clients_data = appt.pop("clients", None) or {}
            appt["client_name"] = (
                clients_data.get("full_name", "לא ידוע")
                if isinstance(clients_data, dict)
                else "לא ידוע"
            )
            appointments.append(appt)

        return {
            "appointments_today": appointments,
            "total_appointments_today": len(appointments),
            "total_revenue_today": sum(p["amount"] for p in (payments_result.data or [])),
            "new_clients_this_month": len(clients_result.data or []),
        }
