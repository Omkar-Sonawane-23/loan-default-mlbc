import pytest


def test_monitoring_reports_insufficient_data_without_inventing_health(client, ml_model_available):
    if not ml_model_available:
        pytest.skip("ML model not trained yet")
    response = client.get("/api/model-monitoring/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "INSUFFICIENT_DATA"
    assert body["recent_prediction_count"] == 0
    assert body["prediction_drift_psi"] is None
    assert body["label_performance"].startswith("PENDING")
    assert body["feature_drift"].startswith("UNAVAILABLE")
