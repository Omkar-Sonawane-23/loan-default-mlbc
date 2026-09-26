"""
ml_service.py

Loads the real trained scikit-learn pipeline (produced by
ml/scripts/train_model.py) and exposes prediction + model-info helpers to
the rest of the backend. No fake/hardcoded predictions are used here --
every call to predict() runs actual model inference.
"""
import json
import os
import threading

import joblib
import pandas as pd

from app.config import settings

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FEATURE_COLUMNS = [
    "age", "annual_income", "employment_years", "credit_score", "loan_amount",
    "loan_term_months", "existing_debt", "debt_to_income_ratio",
    "number_of_previous_loans", "previous_default", "dependents",
    "savings_amount", "employment_type", "requested_loan_purpose",
]

RISK_THRESHOLDS = {"LOW_MAX": 0.30, "MEDIUM_MAX": 0.70}


class MLService:
    _lock = threading.Lock()

    def __init__(self):
        model_path = os.path.normpath(os.path.join(_BASE_DIR, settings.MODEL_PATH))
        metadata_path = os.path.normpath(os.path.join(_BASE_DIR, settings.MODEL_METADATA_PATH))

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"ML model not found at {model_path}. "
                "Run `python ml/scripts/generate_demo_data.py` then "
                "`python ml/scripts/train_model.py` first."
            )

        self.pipeline = joblib.load(model_path)
        with open(metadata_path) as f:
            self.metadata = json.load(f)

        # Comparison report (optional, for /api/model/metrics)
        comparison_path = os.path.normpath(
            os.path.join(_BASE_DIR, "..", "ml", "reports", "model_comparison.json")
        )
        self.comparison = {}
        if os.path.exists(comparison_path):
            with open(comparison_path) as f:
                self.comparison = json.load(f)

    @property
    def model_name(self) -> str:
        return self.metadata["model_name"]

    @property
    def model_version(self) -> str:
        return self.metadata["model_version"]

    @property
    def feature_importance(self) -> list:
        return self.metadata.get("feature_importance", [])

    @property
    def metrics(self) -> dict:
        return self.metadata.get("metrics", {})

    @property
    def info(self) -> dict:
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "trained_at": self.metadata.get("trained_at"),
            "dataset_size": self.metadata.get("dataset_size"),
            "features": self.metadata.get("features"),
            "candidate_models_compared": self.metadata.get("candidate_models_compared"),
            "feature_importance_method": self.metadata.get("feature_importance_method"),
            "notice": self.metadata.get("notice"),
        }

    @staticmethod
    def classify_risk(default_probability: float) -> str:
        if default_probability < RISK_THRESHOLDS["LOW_MAX"]:
            return "LOW"
        elif default_probability < RISK_THRESHOLDS["MEDIUM_MAX"]:
            return "MEDIUM"
        return "HIGH"

    def predict(self, features: dict) -> dict:
        with self._lock:
            row = pd.DataFrame([{col: features.get(col) for col in FEATURE_COLUMNS}])
            proba = self.pipeline.predict_proba(row)[0]

        default_probability = round(float(proba[1]), 4)
        non_default_probability = round(float(proba[0]), 4)
        risk_category = self.classify_risk(default_probability)

        # Top contributing factors, taken from the model's real (global)
        # feature importance -- documented as global, not per-instance,
        # explanation in the API response.
        risk_factors = [
            {"feature": self._humanize(f["feature"]), "importance": f["importance"]}
            for f in self.feature_importance[:5]
        ]

        return {
            "prediction": 1 if default_probability >= 0.5 else 0,
            "default_probability": default_probability,
            "non_default_probability": non_default_probability,
            "risk_category": risk_category,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "risk_factors": risk_factors,
            "disclaimer": settings.ACADEMIC_DISCLAIMER,
        }

    @staticmethod
    def _humanize(raw_feature_name: str) -> str:
        name = raw_feature_name.split("__", 1)[-1]
        name = name.replace("_", " ").title()
        return name


_instance: MLService | None = None
_instance_lock = threading.Lock()


def get_ml_service() -> MLService:
    global _instance
    if _instance is None:
        with _instance_lock:
            if _instance is None:
                _instance = MLService()
    return _instance
