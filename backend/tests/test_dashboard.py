"""
טסטים ל-endpoint של הדשבורד.
"""

DASHBOARD_STUB = {
    "appointments_today": [
        {
            "id": "22222222-2222-2222-2222-222222222222",
            "client_id": "11111111-1111-1111-1111-111111111111",
            "client_name": "שרה כהן",
            "treatment_name": "ניקוי פנים",
            "start_time": "2024-06-15T10:00:00+00:00",
            "end_time": "2024-06-15T11:00:00+00:00",
            "price": 150.0,
            "status": "scheduled",
            "notes": None,
            "created_at": "2024-01-15T10:00:00+00:00",
            "updated_at": "2024-01-15T10:00:00+00:00",
        }
    ],
    "total_appointments_today": 1,
    "total_revenue_today": 200.0,
    "new_clients_this_month": 5,
}


def test_dashboard_today_returns_200(client, monkeypatch):
    from app.api import dashboard as api_dashboard
    monkeypatch.setattr(api_dashboard.service, "get_today_summary", lambda: DASHBOARD_STUB)

    resp = client.get("/api/dashboard/today")
    assert resp.status_code == 200


def test_dashboard_today_structure(client, monkeypatch):
    from app.api import dashboard as api_dashboard
    monkeypatch.setattr(api_dashboard.service, "get_today_summary", lambda: DASHBOARD_STUB)

    body = client.get("/api/dashboard/today").json()

    assert "appointments_today" in body
    assert "total_appointments_today" in body
    assert "total_revenue_today" in body
    assert "new_clients_this_month" in body

    assert isinstance(body["appointments_today"], list)
    assert isinstance(body["total_appointments_today"], int)
    assert isinstance(body["total_revenue_today"], (int, float))
    assert isinstance(body["new_clients_this_month"], int)


def test_dashboard_today_values(client, monkeypatch):
    from app.api import dashboard as api_dashboard
    monkeypatch.setattr(api_dashboard.service, "get_today_summary", lambda: DASHBOARD_STUB)

    body = client.get("/api/dashboard/today").json()

    assert body["total_appointments_today"] == 1
    assert body["total_revenue_today"] == 200.0
    assert body["new_clients_this_month"] == 5


def test_dashboard_appointment_has_client_name(client, monkeypatch):
    from app.api import dashboard as api_dashboard
    monkeypatch.setattr(api_dashboard.service, "get_today_summary", lambda: DASHBOARD_STUB)

    body = client.get("/api/dashboard/today").json()
    appt = body["appointments_today"][0]

    assert "client_name" in appt
    assert appt["client_name"] == "שרה כהן"


def test_dashboard_empty_day(client, monkeypatch):
    from app.api import dashboard as api_dashboard

    empty_stub = {
        "appointments_today": [],
        "total_appointments_today": 0,
        "total_revenue_today": 0.0,
        "new_clients_this_month": 0,
    }
    monkeypatch.setattr(api_dashboard.service, "get_today_summary", lambda: empty_stub)

    body = client.get("/api/dashboard/today").json()
    assert body["total_appointments_today"] == 0
    assert body["total_revenue_today"] == 0.0
    assert body["appointments_today"] == []
