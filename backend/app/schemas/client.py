"""
סכמות (Pydantic) ללקוחות.
שדות הליבה למרפאת טיפולי פנים: פרטים אישיים + מידע רפואי/קוסמטי רלוונטי לטיפול.
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class ClientBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, description="שם מלא")
    phone: str = Field(..., min_length=9, max_length=20, description="מספר טלפון")
    email: Optional[EmailStr] = None
    date_of_birth: Optional[date] = None
    skin_type: Optional[str] = Field(None, description="סוג עור: יבש / שמן / מעורב / רגיש / נורמלי")
    allergies: Optional[str] = Field(None, description="אלרגיות ידועות")
    medical_notes: Optional[str] = Field(None, description="הערות רפואיות כלליות (תרופות, הריון, רגישויות)")
    referral_source: Optional[str] = Field(None, description="איך הגיעה אלינו (חברה, אינסטגרם, גוגל...)")
    general_notes: Optional[str] = Field(None, description="הערות כלליות חופשיות")


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, min_length=9, max_length=20)
    email: Optional[EmailStr] = None
    date_of_birth: Optional[date] = None
    skin_type: Optional[str] = None
    allergies: Optional[str] = None
    medical_notes: Optional[str] = None
    referral_source: Optional[str] = None
    general_notes: Optional[str] = None
    is_active: Optional[bool] = None


class ClientOut(ClientBase):
    id: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
