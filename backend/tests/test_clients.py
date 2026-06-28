"""
טסטים ליצירה ומחיקת לקוחות.
שירותי Supabase מוחלפים ב-monkeypatch - אין גישה לרשת.
"""
import pytest
from fastapi import HTTPException

CLIENT_STUB = {
    "id": "11111111-1111-1111-1111-111111111111",
    "full_name": "שרה כהן",
    "phone": "0501234567",
    "email": None,
    "date_of_birth": None,
    "skin_type": None,
    "allergies": None,
    "medical_notes": None,
    "referral_source": None,
    "general_notes": None,
    "is_active": True,
    "created_at": "2024-01-15T10:00:00+00:00",
    "updated_at": "2024-01-15T10:00:00+00:00",
}


# --- יצירת לקוחה ---

def test_create_client_valid(client, monkeypatch):
    from app.api import clients as api_clients
    monkeypatch.setattr(api_clients.service, "create_client", lambda payload: CLIENT_STUB)

    resp = client.post("/api/clients/", json={"full_name": "שרה כהן", "phone": "0501234567"})
    assert resp.status_code == 201
    assert resp.json()["full_name"] == "שרה כהן"
    assert resp.json()["is_active"] is True


def test_create_client_phone_too_short(client):
    # 3 תווים בלבד - Pydantic min_length=9 → 422
    resp = client.post("/api/clients/", json={"full_name": "שרה כהן", "phone": "123"})
    assert resp.status_code == 422
    body = resp.json()
    assert "error" in body  # גלובל handler מחזיר מפתח "error"


def test_create_client_name_too_short(client):
    # שם קצר מ-2 תווים → 422
    resp = client.post("/api/clients/", json={"full_name": "א", "phone": "0501234567"})
    assert resp.status_code == 422


def test_create_client_missing_required_fields(client):
    resp = client.post("/api/clients/", json={"full_name": "שרה כהן"})  # חסר phone
    assert resp.status_code == 422


# --- מחיקת לקוחה ---

def test_delete_client_with_future_appointments_raises_409(client, monkeypatch):
    from app.api import clients as api_clients

    def mock_delete(client_id, force=False):
        raise HTTPException(
            status_code=409,
            detail="ללקוחה יש 2 תורים עתידיים פתוחים. בטלי אותם קודם.",
        )

    monkeypatch.setattr(api_clients.service, "delete_client", mock_delete)
    resp = client.delete("/api/clients/11111111-1111-1111-1111-111111111111")
    assert resp.status_code == 409
    assert "תורים עתידיים" in resp.json()["detail"]


def test_delete_client_force_bypasses_check(client, monkeypatch):
    from app.api import clients as api_clients

    received_args: list[dict] = []

    def mock_delete(client_id, force=False):
        received_args.append({"client_id": client_id, "force": force})
        return True

    monkeypatch.setattr(api_clients.service, "delete_client", mock_delete)
    resp = client.delete(
        "/api/clients/11111111-1111-1111-1111-111111111111?force=true"
    )
    assert resp.status_code == 204
    assert received_args[0]["force"] is True
