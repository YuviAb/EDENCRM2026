"""
טסטים לתורים: ולידציית זמנים, בדיקת חפיפות.
"""
import pytest
from datetime import datetime, timezone
from fastapi import HTTPException

APPT_STUB = {
    "id": "22222222-2222-2222-2222-222222222222",
    "client_id": "11111111-1111-1111-1111-111111111111",
    "treatment_name": "ניקוי פנים",
    "start_time": "2025-06-15T10:00:00+00:00",
    "end_time": "2025-06-15T11:00:00+00:00",
    "price": 150.0,
    "status": "scheduled",
    "notes": None,
    "created_at": "2024-01-15T10:00:00+00:00",
    "updated_at": "2024-01-15T10:00:00+00:00",
}

VALID_PAYLOAD = {
    "client_id": "11111111-1111-1111-1111-111111111111",
    "treatment_name": "ניקוי פנים",
    "start_time": "2025-06-15T10:00:00+00:00",
    "end_time": "2025-06-15T11:00:00+00:00",
    "price": 150.0,
}


# --- unit tests: ולידציית זמנים ישירות על הפונקציה (ללא רשת) ---

def test_time_validity_end_before_start():
    from app.services.appointment_service import _check_time_validity

    start = datetime(2024, 6, 15, 11, 0, tzinfo=timezone.utc)
    end = datetime(2024, 6, 15, 10, 0, tzinfo=timezone.utc)
    with pytest.raises(HTTPException) as exc_info:
        _check_time_validity(start, end)
    assert exc_info.value.status_code == 400
    assert "סיום" in exc_info.value.detail


def test_time_validity_equal_times():
    from app.services.appointment_service import _check_time_validity

    dt = datetime(2024, 6, 15, 10, 0, tzinfo=timezone.utc)
    with pytest.raises(HTTPException) as exc_info:
        _check_time_validity(dt, dt)
    assert exc_info.value.status_code == 400


def test_time_validity_valid_range():
    from app.services.appointment_service import _check_time_validity

    start = datetime(2024, 6, 15, 10, 0, tzinfo=timezone.utc)
    end = datetime(2024, 6, 15, 11, 0, tzinfo=timezone.utc)
    _check_time_validity(start, end)  # לא אמורה לזרוק


# --- integration tests: דרך TestClient עם mock ---

def test_create_appointment_valid(client, monkeypatch):
    from app.api import appointments as api_appts
    monkeypatch.setattr(api_appts.service, "create_appointment", lambda payload: APPT_STUB)

    resp = client.post("/api/appointments/", json=VALID_PAYLOAD)
    assert resp.status_code == 201
    assert resp.json()["treatment_name"] == "ניקוי פנים"
    assert resp.json()["status"] == "scheduled"


def test_create_appointment_overlap_returns_409(client, monkeypatch):
    from app.api import appointments as api_appts

    def mock_create(payload):
        raise HTTPException(
            status_code=409,
            detail="קיים תור חופף: שרה כהן ב-15/06/2025 10:00. יש לבטל אותו קודם.",
        )

    monkeypatch.setattr(api_appts.service, "create_appointment", mock_create)
    resp = client.post("/api/appointments/", json=VALID_PAYLOAD)
    assert resp.status_code == 409
    assert "חופף" in resp.json()["detail"]


def test_create_appointment_end_before_start_returns_400(client, monkeypatch):
    from app.api import appointments as api_appts

    def mock_create(payload):
        raise HTTPException(status_code=400, detail="שעת הסיום חייבת להיות אחרי שעת ההתחלה")

    monkeypatch.setattr(api_appts.service, "create_appointment", mock_create)
    bad_payload = {**VALID_PAYLOAD, "start_time": "2025-06-15T11:00:00+00:00", "end_time": "2025-06-15T10:00:00+00:00"}
    resp = client.post("/api/appointments/", json=bad_payload)
    assert resp.status_code == 400
    assert "סיום" in resp.json()["detail"]
