"""
נקודות קצה (endpoints) לניהול לקוחות.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.schemas.client import ClientCreate, ClientUpdate, ClientOut
from app.services.client_service import ClientService

router = APIRouter(prefix="/clients", tags=["Clients"])
service = ClientService()


@router.get("/", response_model=list[ClientOut])
def list_clients(
    search: Optional[str] = Query(None, description="חיפוש לפי שם או טלפון"),
    active_only: bool = Query(True, description="הצג רק לקוחות פעילות"),
):
    return service.list_clients(search=search, active_only=active_only)


@router.get("/{client_id}", response_model=ClientOut)
def get_client(client_id: str):
    client = service.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="לקוחה לא נמצאה")
    return client


@router.post("/", response_model=ClientOut, status_code=201)
def create_client(payload: ClientCreate):
    return service.create_client(payload)


@router.patch("/{client_id}", response_model=ClientOut)
def update_client(client_id: str, payload: ClientUpdate):
    updated = service.update_client(client_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="לקוחה לא נמצאה")
    return updated


@router.delete("/{client_id}", status_code=204)
def delete_client(
    client_id: str,
    force: bool = Query(False, description="מחק גם אם יש תורים עתידיים פתוחים"),
):
    success = service.delete_client(client_id, force=force)
    if not success:
        raise HTTPException(status_code=404, detail="לקוחה לא נמצאה")
