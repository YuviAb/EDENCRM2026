from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class TreatmentIn(BaseModel):
    treatment_date: date
    treatment_type: str = Field(..., min_length=1)
    notes: Optional[str] = None


class TreatmentUpdate(BaseModel):
    treatment_date: Optional[date] = None
    treatment_type: Optional[str] = None
    notes: Optional[str] = None


class TreatmentOut(BaseModel):
    id: str
    client_id: str
    treatment_date: date
    treatment_type: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
