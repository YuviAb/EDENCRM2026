from fastapi import APIRouter, Header, HTTPException, status

from app.schemas.intake import IntakeFormIn, IntakeFormResult
from app.services.intake_service import process_intake
from app.core.config import settings

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
