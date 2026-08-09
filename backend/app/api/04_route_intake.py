# app/api/intake.py
# ה-Endpoint שמקבל טפסים מ-Netlify. מוגן במפתח סודי.

import os
from fastapi import APIRouter, Header, HTTPException, status

from app.schemas.intake import IntakeFormIn, IntakeFormResult
from app.services.intake_service import process_intake

router = APIRouter(prefix="/api/intake", tags=["intake"])

# מפתח סודי משותף בין Netlify ל-CRM (שמור כמשתנה סביבה)
INTAKE_SECRET = os.environ.get("INTAKE_SECRET", "")


@router.post("/anamneza", response_model=IntakeFormResult)
def receive_anamneza(
    payload: IntakeFormIn,
    x_intake_secret: str = Header(None, alias="X-Intake-Secret"),
):
    # --- אבטחה: רק בקשות עם המפתח הנכון מתקבלות ---
    if not INTAKE_SECRET or x_intake_secret != INTAKE_SECRET:
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
