"""
נקודות קצה לתמונות לקוחות - העלאה, צפייה, מחיקה.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.services.photo_service import PhotoService

router = APIRouter(prefix="/photos", tags=["Client Photos"])
service = PhotoService()


@router.get("/client/{client_id}")
def list_client_photos(client_id: str):
    return service.list_photos(client_id)


@router.post("/client/{client_id}/upload", status_code=201)
async def upload_photo(
    client_id: str,
    file: UploadFile = File(...),
    caption: Optional[str] = Form(None),
    appointment_id: Optional[str] = Form(None),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="יש להעלות קובץ תמונה בלבד")

    file_bytes = await file.read()
    result = service.upload_photo(
        client_id=client_id,
        file_bytes=file_bytes,
        filename=file.filename or "photo.jpg",
        content_type=file.content_type,
        caption=caption,
        appointment_id=appointment_id,
    )
    return result


@router.delete("/{photo_id}", status_code=204)
def delete_photo(photo_id: str):
    success = service.delete_photo(photo_id)
    if not success:
        raise HTTPException(status_code=404, detail="תמונה לא נמצאה")
