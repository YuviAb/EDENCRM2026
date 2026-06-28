from fastapi import APIRouter
from app.services.daily_reminder_service import send_daily_reminder

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/test-daily-reminder")
def test_daily_reminder():
    """
    מפעיל את תזכורת הבוקר באופן מיידי (לבדיקה — לא ממתין ל-06:00).
    יחזיר את ההודעה שנשלחה + האם השליחה הצליחה.
    """
    success, body = send_daily_reminder()
    return {
        "sent":    success,
        "message": body,
        "status":  "נשלח בהצלחה ✓" if success else "לא נשלח — בדוק הגדרות TWILIO_* ב-.env",
    }
