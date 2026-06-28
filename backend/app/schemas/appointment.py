"""
סכמות לתורים/פגישות ביומן.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class AppointmentStatus(str, Enum):
    scheduled = "scheduled"      # נקבע
    confirmed = "confirmed"      # אושר ע"י הלקוחה
    completed = "completed"      # הושלם
    cancelled = "cancelled"      # בוטל
    no_show = "no_show"          # לא הגיעה


class AppointmentBase(BaseModel):
    client_id: str
    treatment_name: str = Field(..., description="סוג הטיפול, למשל: ניקוי פנים, מיקרודרמהברזיה")
    start_time: datetime
    end_time: datetime
    price: Optional[float] = Field(None, ge=0, description="מחיר הטיפול לתור הזה")
    status: AppointmentStatus = AppointmentStatus.scheduled
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    treatment_name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    price: Optional[float] = Field(None, ge=0)
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None


class AppointmentOut(AppointmentBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
