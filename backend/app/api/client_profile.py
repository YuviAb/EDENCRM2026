"""
תיק לקוח: טיפולים ומדיה (תמונות/סרטונים).
Routes: /clients/{client_id}/treatments  and  /clients/{client_id}/media
"""
import uuid
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.core.supabase_client import get_supabase_admin
from app.core.config import settings
from app.schemas.treatment import TreatmentIn, TreatmentUpdate, TreatmentOut

router = APIRouter(prefix="/clients", tags=["client-profile"])

BUCKET = settings.SUPABASE_STORAGE_BUCKET  # "client-photos"


# ── Treatments ────────────────────────────────────────────────────────

@router.get("/{client_id}/treatments", response_model=list[TreatmentOut])
def list_treatments(client_id: str):
    sb = get_supabase_admin()
    result = (
        sb.table("treatments")
        .select("*")
        .eq("client_id", client_id)
        .order("treatment_date", desc=True)
        .execute()
    )
    return result.data


@router.post("/{client_id}/treatments", response_model=TreatmentOut, status_code=201)
def add_treatment(client_id: str, payload: TreatmentIn):
    sb = get_supabase_admin()
    data = payload.model_dump(mode="json")
    data["client_id"] = client_id
    result = sb.table("treatments").insert(data).execute()
    return result.data[0]


@router.patch("/{client_id}/treatments/{treatment_id}", response_model=TreatmentOut)
def update_treatment(client_id: str, treatment_id: str, payload: TreatmentUpdate):
    sb = get_supabase_admin()
    data = payload.model_dump(exclude_unset=True, mode="json")
    if not data:
        r = sb.table("treatments").select("*").eq("id", treatment_id).maybe_single().execute()
        return r.data
    result = (
        sb.table("treatments")
        .update(data)
        .eq("id", treatment_id)
        .eq("client_id", client_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="טיפול לא נמצא")
    return result.data[0]


@router.delete("/{client_id}/treatments/{treatment_id}", status_code=204)
def delete_treatment(client_id: str, treatment_id: str):
    sb = get_supabase_admin()
    result = (
        sb.table("treatments")
        .delete()
        .eq("id", treatment_id)
        .eq("client_id", client_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="טיפול לא נמצא")


# ── Media ─────────────────────────────────────────────────────────────

@router.get("/{client_id}/media")
def list_media(client_id: str):
    sb = get_supabase_admin()
    result = (
        sb.table("client_photos")
        .select("*")
        .eq("client_id", client_id)
        .order("created_at", desc=True)
        .execute()
    )
    items = result.data
    for item in items:
        item["public_url"] = sb.storage.from_(BUCKET).get_public_url(item["storage_path"])
    return items


@router.post("/{client_id}/media", status_code=201)
async def upload_media(
    client_id: str,
    file: UploadFile = File(...),
    caption: str = Form(None),
    media_type: str = Form("image"),
):
    sb = get_supabase_admin()
    ext = file.filename.split(".")[-1] if "." in (file.filename or "") else "jpg"
    storage_path = f"{client_id}/{uuid.uuid4()}.{ext}"
    file_bytes = await file.read()
    sb.storage.from_(BUCKET).upload(
        path=storage_path,
        file=file_bytes,
        file_options={"content-type": file.content_type or "application/octet-stream"},
    )
    row = {
        "client_id": client_id,
        "storage_path": storage_path,
        "media_type": media_type,
    }
    if caption:
        row["caption"] = caption
    result = sb.table("client_photos").insert(row).execute()
    record = result.data[0]
    record["public_url"] = sb.storage.from_(BUCKET).get_public_url(storage_path)
    return record


@router.delete("/{client_id}/media/{media_id}", status_code=204)
def delete_media(client_id: str, media_id: str):
    sb = get_supabase_admin()
    record = (
        sb.table("client_photos")
        .select("storage_path")
        .eq("id", media_id)
        .eq("client_id", client_id)
        .maybe_single()
        .execute()
    )
    if not record or not record.data:
        raise HTTPException(status_code=404, detail="קובץ לא נמצא")
    try:
        sb.storage.from_(BUCKET).remove([record.data["storage_path"]])
    except Exception:
        pass
    sb.table("client_photos").delete().eq("id", media_id).execute()
