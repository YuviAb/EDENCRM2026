# app/services/intake_service.py
# הלוגיקה העסקית: זיהוי לקוחה, יצירה אם צריך, שמירת הטופס וה-PDF.
#
# מודל הזיהוי:
#   1) חיפוש לפי phone_normalized (הטלפון הוא הזיהוי העיקרי).
#   2) אם יש כמה התאמות - מצמצמים לפי full_name.
#   3) אם לא נמצא - יוצרים לקוחה חדשה.

import base64
import re
import uuid
from datetime import datetime, timezone

from app.core.supabase_client import supabase  # ה-client הקיים שלך
from app.schemas.intake import IntakeFormIn, IntakeFormResult


def _normalize_phone(phone: str) -> str:
    """מסיר כל תו שאינו ספרה — לזיהוי גמיש."""
    return re.sub(r"[^0-9]", "", phone or "")


def _compose_full_name(first: str | None, last: str | None) -> str:
    """מרכיב full_name מהשדות שהגיעו מהטופס."""
    return " ".join(p for p in [(first or "").strip(), (last or "").strip()] if p)


def _names_match(a: str, b: str) -> bool:
    """השוואת שמות רכה - מתעלמת מרווחים מיותרים ורגישות רישיות."""
    def norm(s: str) -> str:
        return re.sub(r"\s+", " ", (s or "").strip()).lower()
    return norm(a) == norm(b)


def _find_client(first_name: str | None, last_name: str | None, phone: str):
    """
    מחפש לקוחה לפי טלפון מנורמל + אימות שם.
    מחזיר את רשומת הלקוחה או None.
    """
    normalized = _normalize_phone(phone)
    if not normalized:
        return None

    resp = (
        supabase.table("clients")
        .select("*")
        .eq("phone_normalized", normalized)
        .execute()
    )
    rows = resp.data or []

    if not rows:
        return None

    # התאמה יחידה - זו הלקוחה
    if len(rows) == 1:
        return rows[0]

    # כמה לקוחות עם אותו טלפון - מצמצמים לפי השם המלא
    submitted_full_name = _compose_full_name(first_name, last_name)
    if submitted_full_name:
        for row in rows:
            if _names_match(row.get("full_name", ""), submitted_full_name):
                return row

    # לא הצלחנו לצמצם - מחזירים את הראשון (עדיף מלייצר כפילות)
    return rows[0]


def _create_client(first_name: str | None, last_name: str | None, phone: str) -> dict:
    """יוצר לקוחה חדשה כשלא נמצאה התאמה."""
    full_name = _compose_full_name(first_name, last_name) or "ללא שם"
    new_client = {
        "full_name": full_name,
        "phone": (phone or "").strip() or None,
        "is_active": True,
    }
    resp = supabase.table("clients").insert(new_client).execute()
    return resp.data[0]


def _upload_pdf(client_id: str, pdf_base64: str | None) -> str | None:
    """מעלה את ה-PDF ל-Supabase Storage ומחזיר את הנתיב."""
    if not pdf_base64:
        return None
    try:
        pdf_bytes = base64.b64decode(pdf_base64)
    except Exception:
        return None

    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    path = f"{client_id}/anamneza-{ts}-{uuid.uuid4().hex[:8]}.pdf"

    supabase.storage.from_("client-forms").upload(
        path,
        pdf_bytes,
        {"content-type": "application/pdf", "upsert": "false"},
    )
    return path


def process_intake(payload: IntakeFormIn) -> IntakeFormResult:
    """הפונקציה הראשית — מזהה/יוצר לקוחה, שומר טופס + PDF."""

    # 1) זיהוי הלקוחה
    client = _find_client(payload.first_name, payload.last_name, payload.phone)
    client_created = False

    # 2) אם לא נמצאה - יוצרים חדשה
    if client is None:
        client = _create_client(payload.first_name, payload.last_name, payload.phone)
        client_created = True

    client_id = client["id"]

    # 3) העלאת ה-PDF (אם קיים)
    pdf_path = _upload_pdf(client_id, payload.pdf_base64)

    # 4) שמירת רשומת הטופס
    form_row = {
        "client_id": client_id,
        "submitted_first_name": payload.first_name,
        "submitted_last_name": payload.last_name,
        "submitted_phone": payload.phone,
        "form_data": payload.form_data,
        "pdf_path": pdf_path,
        "auto_created_client": client_created,
    }
    form_resp = supabase.table("client_forms").insert(form_row).execute()
    form_id = form_resp.data[0]["id"]

    return IntakeFormResult(
        ok=True,
        client_id=str(client_id),
        form_id=str(form_id),
        client_created=client_created,
        message=(
            "נוצרה לקוחה חדשה והטופס שויך אליה"
            if client_created
            else "הטופס שויך ללקוחה קיימת"
        ),
    )
