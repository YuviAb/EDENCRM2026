"""
שירות תמונות לקוחות: העלאת קבצים ל-Supabase Storage + שמירת מטא-דאטה בטבלה.
"""
import uuid
from typing import Optional
from app.core.supabase_client import get_supabase_admin
from app.core.config import settings
from app.schemas.photo import ClientPhotoCreate

TABLE = "client_photos"


class PhotoService:
    def __init__(self):
        self.db = get_supabase_admin()
        self.bucket = settings.SUPABASE_STORAGE_BUCKET

    def _build_storage_path(self, client_id: str, filename: str) -> str:
        ext = filename.split(".")[-1] if "." in filename else "jpg"
        unique_name = f"{uuid.uuid4()}.{ext}"
        return f"{client_id}/{unique_name}"

    def upload_photo(
        self,
        client_id: str,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        caption: Optional[str] = None,
        appointment_id: Optional[str] = None,
    ) -> dict:
        storage_path = self._build_storage_path(client_id, filename)

        # העלאה ל-Storage
        self.db.storage.from_(self.bucket).upload(
            path=storage_path,
            file=file_bytes,
            file_options={"content-type": content_type},
        )

        # שמירת מטא-דאטה בטבלה
        photo_data = ClientPhotoCreate(
            client_id=client_id,
            appointment_id=appointment_id,
            storage_path=storage_path,
            caption=caption,
        )
        result = self.db.table(TABLE).insert(photo_data.model_dump(exclude_none=True, mode="json")).execute()
        record = result.data[0]
        record["public_url"] = self.get_public_url(storage_path)
        return record

    def get_public_url(self, storage_path: str) -> str:
        return self.db.storage.from_(self.bucket).get_public_url(storage_path)

    def list_photos(self, client_id: str) -> list[dict]:
        result = self.db.table(TABLE).select("*").eq("client_id", client_id).order("created_at", desc=True).execute()
        photos = result.data
        for photo in photos:
            photo["public_url"] = self.get_public_url(photo["storage_path"])
        return photos

    def delete_photo(self, photo_id: str) -> bool:
        record = self.db.table(TABLE).select("storage_path").eq("id", photo_id).maybe_single().execute()
        if not record or not record.data:
            return False
        storage_path = record.data["storage_path"]
        self.db.storage.from_(self.bucket).remove([storage_path])
        result = self.db.table(TABLE).delete().eq("id", photo_id).execute()
        return bool(result.data)
