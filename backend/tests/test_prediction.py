import pytest
from tests.conftest import SAMPLE_FEATURES


def test_prediction_endpoint_returns_real_scores(client, ml_model_available):
    if not ml_model_available:
        pytest.skip("ML model not trained yet - run ml/scripts/train_model.py first")

    response = client.post("/api/predictions", json={"input_features": SAMPLE_FEATURES})
    assert response.status_code == 200
    data = response.json()

    assert 0.0 <= data["default_probability"] <= 1.0
    assert 0.0 <= data["non_default_probability"] <= 1.0
    assert round(data["default_probability"] + data["non_default_probability"], 4) == 1.0
    assert data["risk_category"] in ("LOW", "MEDIUM", "HIGH")
    assert data["model_name"]
    assert data["model_version"]
    assert "disclaimer" in data
    assert isinstance(data["risk_factors"], list)
    assert 0 <= data["credit_score"] <= 1000
    assert data["credit_score"] == round((1 - data["default_probability"]) * 1000)
    assert len(data["model_hash"]) == 64
    assert data["expected_loss"] >= 0
    assert data["expected_loss"] == pytest.approx(data["default_probability"] * 0.45 * SAMPLE_FEATURES["loan_amount"], abs=0.01)
    assert data["expected_loss_assumptions"]["formula"] == "PD × LGD × EAD"
    assert "synthetic" in data["credit_score_validity"].lower()
    assert "calibrated" in data["credit_score_method"].lower()
    assert data["storage_status"] in ("STORED", "UNAVAILABLE")
    assert "not a local explanation" in data["explanation_scope"]
    assert data["local_explanation"]["method"] == "SHAP"
    assert data["local_explanation"]["status"] == "AVAILABLE"
    assert data["local_explanation"]["contributors"]


def test_prediction_is_logged_for_monitoring(client, ml_model_available):
    if not ml_model_available:
        pytest.skip("ML model not trained yet")
    response = client.post("/api/predictions", json={"input_features": SAMPLE_FEATURES})
    assert response.status_code == 200
    # The test client database is injected through FastAPI dependency overrides.
    from app.dependencies import get_database
    db = client.app.dependency_overrides[get_database]()
    event = db.model_predictions.find_one()
    assert event is not None
    assert event["data_source"] == "user_provided"
    assert event["prediction"]["model_version"]


def test_prediction_rejects_invalid_credit_score(client):
    bad_features = dict(SAMPLE_FEATURES)
    bad_features["credit_score"] = 9999  # out of allowed 300-900 range
    response = client.post("/api/predictions", json={"input_features": bad_features})
    assert response.status_code == 422


def test_prediction_rejects_negative_loan_amount(client):
    bad_features = dict(SAMPLE_FEATURES)
    bad_features["loan_amount"] = -1000
    response = client.post("/api/predictions", json={"input_features": bad_features})
    assert response.status_code == 422


def test_higher_risk_profile_scores_higher_default_probability(client, ml_model_available):
    if not ml_model_available:
        pytest.skip("ML model not trained yet")

    good_profile = dict(SAMPLE_FEATURES)
    good_profile.update({"credit_score": 820, "debt_to_income_ratio": 0.1, "previous_default": 0})

    risky_profile = dict(SAMPLE_FEATURES)
    risky_profile.update({"credit_score": 400, "debt_to_income_ratio": 1.5, "previous_default": 1,
                           "employment_type": "Unemployed"})

    good_resp = client.post("/api/predictions", json={"input_features": good_profile}).json()
    risky_resp = client.post("/api/predictions", json={"input_features": risky_profile}).json()

    assert risky_resp["default_probability"] > good_resp["default_probability"]
