import pytest
from tests.conftest import SAMPLE_FEATURES


def _create_application(client):
    return client.post("/api/applications", json={
        "input_features": SAMPLE_FEATURES,
        "applicant_reference": "APP-TEST-001",
    })


def test_create_application_runs_real_prediction_and_persists(client, ml_model_available):
    if not ml_model_available:
        pytest.skip("ML model not trained yet")

    response = _create_application(client)
    assert response.status_code == 201
    data = response.json()
    assert data["application_id"].startswith("LN-")
    assert data["risk_category"] in ("LOW", "MEDIUM", "HIGH")
    assert data["status"] == "ASSESSED"
    assert data["blockchain"]["registered"] is False


def test_get_application_by_id(client, ml_model_available):
    if not ml_model_available:
        pytest.skip("ML model not trained yet")

    created = _create_application(client).json()
    response = client.get(f"/api/applications/{created['application_id']}")
    assert response.status_code == 200
    assert response.json()["application_id"] == created["application_id"]


def test_get_nonexistent_application_returns_404(client):
    response = client.get("/api/applications/LN-999999")
    assert response.status_code == 404


def test_list_applications_returns_pagination_metadata(client, ml_model_available):
    if not ml_model_available:
        pytest.skip("ML model not trained yet")

    _create_application(client)
    _create_application(client)

    response = client.get("/api/applications?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    assert data["page"] == 1
    assert len(data["items"]) >= 2


def test_update_application_status(client, ml_model_available):
    if not ml_model_available:
        pytest.skip("ML model not trained yet")

    created = _create_application(client).json()
    response = client.patch(
        f"/api/applications/{created['application_id']}/status",
        json={"status": "UNDER_REVIEW"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "UNDER_REVIEW"


def test_update_application_status_is_audited(client, ml_model_available):
    if not ml_model_available:
        pytest.skip("ML model not trained yet")

    created = _create_application(client).json()
    client.patch(f"/api/applications/{created['application_id']}/status", json={"status": "CLOSED"})

    audit_response = client.get(f"/api/applications/{created['application_id']}/audit")
    events = [e["event"] for e in audit_response.json()["events"]]
    assert "Status Changed" in events
    assert "Application Created" in events


def test_delete_application(client, ml_model_available):
    if not ml_model_available:
        pytest.skip("ML model not trained yet")

    created = _create_application(client).json()
    response = client.delete(f"/api/applications/{created['application_id']}")
    assert response.status_code == 200
    assert response.json()["deleted"] is True

    follow_up = client.get(f"/api/applications/{created['application_id']}")
    assert follow_up.status_code == 404


def test_search_applications_by_loan_purpose(client, ml_model_available):
    if not ml_model_available:
        pytest.skip("ML model not trained yet")

    _create_application(client)
    response = client.get("/api/applications?search=Home")
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_filter_applications_by_risk_category(client, ml_model_available):
    if not ml_model_available:
        pytest.skip("ML model not trained yet")

    created = _create_application(client).json()
    response = client.get(f"/api/applications?risk_category={created['risk_category']}")
    assert response.status_code == 200
    assert response.json()["total"] >= 1
