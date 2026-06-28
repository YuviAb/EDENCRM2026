"""
נקודות קצה לניהול היומן (תורים).
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentOut
from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["Appointments"])
service = AppointmentService()


@router.get("/", response_model=list[AppointmentOut])
def list_appointments(
    client_id: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None, description="תחילת טווח, לדוגמה לתצוגת שבוע/חודש ביומן"),
    date_to: Optional[datetime] = Query(None, description="סוף טווח"),
):
    return service.list_appointments(client_id=client_id, date_from=date_from, date_to=date_to)


@router.get("/{appointment_id}", response_model=AppointmentOut)
def get_appointment(appointment_id: str):
    appt = service.get_appointment(appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="תור לא נמצא")
    return appt


@router.post("/", response_model=AppointmentOut, status_code=201)
def create_appointment(payload: AppointmentCreate):
    return service.create_appointment(payload)


@router.patch("/{appointment_id}", response_model=AppointmentOut)
def update_appointment(appointment_id: str, payload: AppointmentUpdate):
    updated = service.update_appointment(appointment_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="תור לא נמצא")
    return updated


@router.delete("/{appointment_id}", status_code=204)
def delete_appointment(appointment_id: str):
    success = service.delete_appointment(appointment_id)
    if not success:
        raise HTTPException(status_code=404, detail="תור לא נמצא")
