"""
נקודות קצה לניהול תשלומים.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.schemas.payment import PaymentCreate, PaymentUpdate, PaymentOut
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])
service = PaymentService()


@router.get("/", response_model=list[PaymentOut])
def list_payments(client_id: Optional[str] = Query(None)):
    return service.list_payments(client_id=client_id)


@router.get("/client/{client_id}/total")
def get_client_total(client_id: str):
    return {"client_id": client_id, "total_paid": service.get_client_total(client_id)}


@router.get("/{payment_id}", response_model=PaymentOut)
def get_payment(payment_id: str):
    payment = service.get_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="תשלום לא נמצא")
    return payment


@router.post("/", response_model=PaymentOut, status_code=201)
def create_payment(payload: PaymentCreate):
    return service.create_payment(payload)


@router.patch("/{payment_id}", response_model=PaymentOut)
def update_payment(payment_id: str, payload: PaymentUpdate):
    updated = service.update_payment(payment_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="תשלום לא נמצא")
    return updated


@router.delete("/{payment_id}", status_code=204)
def delete_payment(payment_id: str):
    success = service.delete_payment(payment_id)
    if not success:
        raise HTTPException(status_code=404, detail="תשלום לא נמצא")
