"""
סכמות לתמונות לקוחות (לפני/אחרי, מעקב טיפול).
הקבצים עצמם נשמרים ב-Supabase Storage; כאן רק המטא-דאטה + הנתיב.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ClientPhotoBase(BaseModel):
    client_id: str
    appointment_id: Optional[str] = Field(None, description="קישור לתור שבו צולמה התמונה, אם רלוונטי")
    storage_path: str = Field(..., description="הנתיב בתוך bucket האחסון")
    caption: Optional[str] = Field(None, description="למשל: 'לפני טיפול', 'אחרי שבועיים'")
    taken_at: Optional[datetime] = None


class ClientPhotoCreate(ClientPhotoBase):
    pass


class ClientPhotoOut(ClientPhotoBase):
    id: str
    public_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
