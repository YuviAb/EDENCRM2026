"""
תזכורת יומית: בונה הודעת סיכום תורים בעברית ושולחת אותה ב-WhatsApp.
"""
from datetime import datetime
from zoneinfo import ZoneInfo
from dateutil.parser import parse as parse_dt

from app.core.config import settings
from app.core.supabase_client import get_supabase_admin
from app.services.notifications import get_whatsapp_sender

TZ = ZoneInfo("Asia/Jerusalem")

_DAYS_HE = {
    0: "יום שני",
    1: "יום שלישי",
    2: "יום רביעי",
    3: "יום חמישי",
    4: "יום שישי",
    5: "יום שבת",
    6: "יום ראשון",
}

_MONTHS_HE = {
    1: "ינואר",  2: "פברואר", 3: "מרץ",      4: "אפריל",
    5: "מאי",    6: "יוני",   7: "יולי",     8: "אוגוסט",
    9: "ספטמבר", 10: "אוקטובר", 11: "נובמבר", 12: "דצמבר",
}


def _fmt_time(iso_str: str) -> str:
    """מחזיר HH:MM לפי אזור זמן ישראל."""
    dt = parse_dt(iso_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.astimezone(TZ).strftime("%H:%M")


def build_daily_summary() -> str:
    """
    בונה הודעת סיכום תורים ליום הנוכחי.
    שולף מ-Supabase את כל התורים שאינם מבוטלים, ממיין לפי שעה.
    """
    db = get_supabase_admin()
    now = datetime.now(TZ)
    today_start = now.replace(hour=0,  minute=0,  second=0,  microsecond=0)
    today_end   = now.replace(hour=23, minute=59, second=59, microsecond=999_999)

    result = (
        db.table("appointments")
        .select("*, clients(full_name)")
        .neq("status", "cancelled")
        .gte("start_time", today_start.isoformat())
        .lte("start_time", today_end.isoformat())
        .order("start_time")
        .execute()
    )

    day_label   = _DAYS_HE[now.weekday()]
    date_label  = f"{now.day} ב{_MONTHS_HE[now.month]}"

    # מיון ב-Python כגיבוי (Supabase כבר מחזיר ממוין, אך לא מסתכנים)
    appointments = sorted(result.data or [], key=lambda a: a["start_time"])

    if not appointments:
        return f"בוקר טוב! אין תורים קבועים להיום ({day_label}, {date_label})."

    lines = []
    for appt in appointments:
        time_str     = _fmt_time(appt["start_time"])
        clients_data = appt.get("clients") or {}
        client_name  = clients_data.get("full_name", "לא ידוע") if isinstance(clients_data, dict) else "לא ידוע"
        treatment    = appt.get("treatment_name", "")
        lines.append(f"{time_str} - {client_name} - {treatment}")

    count     = len(appointments)
    count_str = "תור אחד" if count == 1 else f"{count} תורים"

    return (
        f"בוקר טוב! התורים של היום ({day_label}, {date_label}):\n\n"
        + "\n".join(lines)
        + f"\n\nסה\"כ {count_str} היום."
    )


def send_daily_reminder() -> tuple[bool, str]:
    """
    מפעיל את build_daily_summary() ושולח את ההודעה ל-CLINIC_OWNER_WHATSAPP_NUMBER.
    מחזיר (success, body).
    """
    body   = build_daily_summary()
    sender = get_whatsapp_sender()
    success = sender.send_message(to=settings.CLINIC_OWNER_WHATSAPP_NUMBER, body=body)
    return success, body
