"""
נקודת קצה לדשבורד - סיכום יומי של תורים, הכנסות ולקוחות חדשים.
"""
from fastapi import APIRouter
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
service = DashboardService()


@router.get("/today")
def get_today_dashboard():
    return service.get_today_summary()
