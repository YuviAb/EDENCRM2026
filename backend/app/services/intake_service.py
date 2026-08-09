import base64
import re
import uuid
from datetime import datetime, timezone

from app.core.supabase_client import get_supabase_admin
from app.schemas.intake import IntakeFormIn, IntakeFormResult


def _normalize_phone(phone: str) -> str:
    return re.sub(r"[^0-9]", "", phone or "")


def _compose_full_name(first: str | None, last: str | None) -> str:
    return " ".join(p for p in [(first or "").strip(), (last or "").strip()] if p)


def _names_match(a: str, b: str) -> bool:
    def norm(s: str) -> str:
        return re.sub(r"\s+", " ", (s or "").strip()).lower()
    return norm(a) == norm(b)


def _find_client(first_name: str | None, last_name: str | None, phone: str):
    sb = get_supabase_admin()
    normalized = _normalize_phone(phone)
    if not normalized:
        return None

    resp = sb.table("clients").select("*").eq("phone_normalized", normalized).execute()
    rows = resp.data or []

    if not rows:
        return None
    if len(rows) == 1:
        return rows[0]

    submitted_full_name = _compose_full_name(first_name, last_name)
    if submitted_full_name:
        for row in rows:
            if _names_match(row.get("full_name", ""), submitted_full_name):
                return row

    return rows[0]


def _create_client(first_name: str | None, last_name: str | None, phone: str) -> dict:
    sb = get_supabase_admin()
    full_name = _compose_full_name(first_name, last_name) or "ללא שם"
    resp = sb.table("clients").insert({
        "full_name": full_name,
        "phone": (phone or "").strip() or None,
        "is_active": True,
    }).execute()
    return resp.data[0]


def _upload_pdf(client_id: str, pdf_base64: str | None) -> str | None:
    if not pdf_base64:
        return None
    try:
        pdf_bytes = base64.b64decode(pdf_base64)
    except Exception:
        return None

    sb = get_supabase_admin()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    path = f"{client_id}/anamneza-{ts}-{uuid.uuid4().hex[:8]}.pdf"
    sb.storage.from_("client-forms").upload(
        path, pdf_bytes, {"content-type": "application/pdf", "upsert": "false"}
    )
    return path


def process_intake(payload: IntakeFormIn) -> IntakeFormResult:
    client = _find_client(payload.first_name, payload.last_name, payload.phone)
    client_created = False

    if client is None:
        client = _create_client(payload.first_name, payload.last_name, payload.phone)
        client_created = True

    client_id = client["id"]
    pdf_path = _upload_pdf(client_id, payload.pdf_base64)

    sb = get_supabase_admin()
    form_resp = sb.table("client_forms").insert({
        "client_id": client_id,
        "submitted_first_name": payload.first_name,
        "submitted_last_name": payload.last_name,
        "submitted_phone": payload.phone,
        "form_data": payload.form_data,
        "pdf_path": pdf_path,
        "auto_created_client": client_created,
    }).execute()
    form_id = form_resp.data[0]["id"]

    return IntakeFormResult(
        ok=True,
        client_id=str(client_id),
        form_id=str(form_id),
        client_created=client_created,
        message="נוצרה לקוחה חדשה והטופס שויך אליה" if client_created else "הטופס שויך ללקוחה קיימת",
    )
