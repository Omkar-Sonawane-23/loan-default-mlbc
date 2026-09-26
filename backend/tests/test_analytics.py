import pytest
from tests.conftest import SAMPLE_FEATURES


def test_dashboard_stats_on_empty_db_returns_zeros(client):
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    stats = response.json()["stats"]
    assert stats["total_applications"] == 0
    assert stats["total_loan_amount"] == 0


def test_dashboard_stats_reflect_created_applications(client, ml_model_available):
    if not ml_model_available:
        pytest.skip("ML model not trained yet")

    client.post("/api/applications", json={"input_features": SAMPLE_FEATURES})
    client.post("/api/applications", json={"input_features": SAMPLE_FEATURES})

    response = client.get("/api/dashboard/stats")
    stats = response.json()["stats"]
    assert stats["total_applications"] == 2
    assert stats["total_loan_amount"] == SAMPLE_FEATURES["loan_amount"] * 2


def test_analytics_endpoint_structure(client, ml_model_available):
    if not ml_model_available:
        pytest.skip("ML model not trained yet")

    client.post("/api/applications", json={"input_features": SAMPLE_FEATURES})
    response = client.get("/api/analytics")
    assert response.status_code == 200
    data = response.json()
    for key in [
        "risk_distribution", "applications_over_time", "default_probability_distribution",
        "loan_amount_by_risk", "credit_score_by_risk", "employment_type_distribution",
        "loan_purpose_distribution", "blockchain",
    ]:
        assert key in data


def test_model_info_endpoint(client, ml_model_available):
    if not ml_model_available:
        pytest.skip("ML model not trained yet")

    response = client.get("/api/model/info")
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"]
    assert data["model_version"]


def test_model_metrics_endpoint(client, ml_model_available):
    if not ml_model_available:
        pytest.skip("ML model not trained yet")

    response = client.get("/api/model/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "accuracy" in data["metrics"]
    assert "roc_auc" in data["metrics"]
