"""
סכמות לתשלומים. כל תשלום משויך ללקוח, ובאופן אופציונלי לתור מסוים.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class PaymentMethod(str, Enum):
    cash = "cash"                  # מזומן
    credit_card = "credit_card"    # אשראי
    bit = "bit"                    # ביט
    bank_transfer = "bank_transfer"  # העברה בנקאית
    other = "other"


class PaymentBase(BaseModel):
    client_id: str
    appointment_id: Optional[str] = Field(None, description="קישור לתור הרלוונטי, אם קיים")
    amount: float = Field(..., gt=0, description="סכום התשלום")
    method: PaymentMethod = PaymentMethod.cash
    paid_at: datetime
    notes: Optional[str] = None


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    method: Optional[PaymentMethod] = None
    paid_at: Optional[datetime] = None
    notes: Optional[str] = None


class PaymentOut(PaymentBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
