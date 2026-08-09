from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class IntakeFormIn(BaseModel):
    """הנתונים שפונקציית Netlify שולחת ל-CRM."""
    first_name: Optional[str] = Field(None, description="שם פרטי מהטופס")
    last_name: Optional[str] = Field(None, description="שם משפחה מהטופס")
    phone: str = Field(..., description="טלפון - חובה לזיהוי")
    form_data: Dict[str, Any] = Field(..., description="כל שדות הטופס")
    pdf_base64: Optional[str] = Field(None, description="קובץ ה-PDF בקידוד base64")


class IntakeFormResult(BaseModel):
    """מה שה-CRM מחזיר ל-Netlify."""
    ok: bool
    client_id: str
    form_id: str
    client_created: bool
    message: str
