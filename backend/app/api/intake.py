from fastapi import APIRouter, Header, HTTPException, status, Depends

from app.schemas.intake import IntakeFormIn, IntakeFormResult
from app.services.intake_service import process_intake
from app.core.config import settings
from app.core.deps import require_admin
from app.core.supabase_client import get_supabase_admin

router = APIRouter(prefix="/intake", tags=["intake"])


@router.post("/anamneza", response_model=IntakeFormResult)
def receive_anamneza(
    payload: IntakeFormIn,
    x_intake_secret: str = Header(None, alias="X-Intake-Secret"),
):
    if not settings.INTAKE_SECRET or x_intake_secret != settings.INTAKE_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing intake secret",
        )
    try:
        return process_intake(payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process intake: {e}",
        )


@router.get("/forms", dependencies=[Depends(require_admin)])
def get_forms():
    sb = get_supabase_admin()
    result = (
        sb.table("client_forms")
        .select("*, clients(full_name, phone)")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@router.get("/forms/{form_id}/pdf-url", dependencies=[Depends(require_admin)])
def get_pdf_url(form_id: str):
    sb = get_supabase_admin()
    form = sb.table("client_forms").select("pdf_path").eq("id", form_id).single().execute()
    if not form.data or not form.data.get("pdf_path"):
        raise HTTPException(status_code=404, detail="PDF לא נמצא")
    signed = sb.storage.from_("client-forms").create_signed_url(form.data["pdf_path"], 300)
    return {"url": signed["signedURL"]}
