"""
טסטים לשירות התזכורת היומית.
לא שולחים הודעות WhatsApp אמיתיות — הכל מדומה (mock).
"""
from unittest.mock import MagicMock
from app.services import daily_reminder_service as svc


# ── עזר: בונה mock ל-Supabase DB עם רשימת תורים נתונה ──────────────
def _mock_db(data: list):
    m = MagicMock()
    # שרשרת: .table().select().neq().gte().lte().order().execute().data
    (m.table.return_value
      .select.return_value
      .neq.return_value
      .gte.return_value
      .lte.return_value
      .order.return_value
      .execute.return_value
      .data) = data
    return m


# ── נתוני בדיקה ──────────────────────────────────────────────────────
# start_time ב-UTC; 06:00 UTC = 09:00 Israel IDT (UTC+3 בקיץ)
APPT_09 = {
    "id": "a1", "client_id": "c1",
    "treatment_name": "ניקוי פנים",
    "start_time": "2026-06-28T06:00:00+00:00",
    "status": "scheduled",
    "clients": {"full_name": "דנה כהן"},
}
APPT_11 = {
    "id": "a2", "client_id": "c2",
    "treatment_name": "מיקרודרמהברזיה",
    "start_time": "2026-06-28T08:30:00+00:00",   # 11:30 IDT
    "status": "confirmed",
    "clients": {"full_name": "מיכל לוי"},
}
APPT_14 = {
    "id": "a3", "client_id": "c3",
    "treatment_name": "טיפול אנטי אייג'ינג",
    "start_time": "2026-06-28T11:00:00+00:00",   # 14:00 IDT
    "status": "scheduled",
    "clients": {"full_name": "שירה אברהם"},
}


# ── טסטים ────────────────────────────────────────────────────────────

def test_no_appointments(monkeypatch):
    """יום ריק → הודעת בוקר טוב ללא תורים."""
    monkeypatch.setattr(svc, "get_supabase_admin", lambda: _mock_db([]))

    result = svc.build_daily_summary()

    assert "בוקר טוב" in result
    assert "אין תורים" in result


def test_single_appointment(monkeypatch):
    """תור אחד → פורמט נכון עם שם, שעה וסוג טיפול, לשון יחיד."""
    monkeypatch.setattr(svc, "get_supabase_admin", lambda: _mock_db([APPT_09]))

    result = svc.build_daily_summary()

    assert "09:00"     in result
    assert "דנה כהן"   in result
    assert "ניקוי פנים" in result
    assert "תור אחד"   in result    # לשון יחיד — לא "1 תורים"
    assert "אין תורים" not in result


def test_multiple_appointments_sorted(monkeypatch):
    """
    כמה תורים — גם אם ה-mock מחזיר אותם בסדר הפוך,
    הפונקציה ממיינת ב-Python ומחזירה בסדר כרונולוגי.
    """
    monkeypatch.setattr(
        svc, "get_supabase_admin",
        lambda: _mock_db([APPT_14, APPT_11, APPT_09]),  # סדר הפוך בכוונה
    )

    result = svc.build_daily_summary()

    idx_09 = result.index("09:00")
    idx_11 = result.index("11:30")
    idx_14 = result.index("14:00")
    assert idx_09 < idx_11 < idx_14, "תורים חייבים להופיע בסדר כרונולוגי"

    assert "דנה כהן"    in result
    assert "מיכל לוי"   in result
    assert "שירה אברהם" in result
    assert "3 תורים"    in result   # לשון רבים


def test_send_daily_reminder_mocked(monkeypatch):
    """
    send_daily_reminder() קורא ל-get_whatsapp_sender().send_message().
    מוודאים שנשלחה הודעה אחת עם התוכן הנכון — ללא WhatsApp אמיתי.
    """
    monkeypatch.setattr(svc, "get_supabase_admin", lambda: _mock_db([APPT_09]))

    sent: list[dict] = []

    class _MockSender:
        def send_message(self, to: str, body: str) -> bool:
            sent.append({"to": to, "body": body})
            return True

    monkeypatch.setattr(svc, "get_whatsapp_sender", lambda: _MockSender())

    success, body = svc.send_daily_reminder()

    assert success is True
    assert len(sent) == 1
    assert "09:00"   in body
    assert "דנה כהן" in body
