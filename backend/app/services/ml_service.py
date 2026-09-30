"""
ml_service.py

Loads the real trained scikit-learn pipeline (produced by
ml/scripts/train_model.py) and exposes prediction + model-info helpers to
the rest of the backend. No fake/hardcoded predictions are used here --
every call to predict() runs actual model inference.
"""
import json
import os
import hashlib
import threading

import joblib
import pandas as pd
import shap

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

        with open(model_path, "rb") as artifact:
            self.artifact_sha256 = hashlib.sha256(artifact.read()).hexdigest()
        self.pipeline = joblib.load(model_path)
        with open(metadata_path) as f:
            self.metadata = json.load(f)

        # Explain the pre-calibration base estimator on its encoded feature space.
        # SHAP contributions are therefore in the base model's output scale and
        # intentionally are not represented as calibrated-PD deltas.
        self._explain_pipeline = self.pipeline
        if hasattr(self.pipeline, "calibrated_classifiers_"):
            self._explain_pipeline = self.pipeline.calibrated_classifiers_[0].estimator
        self._explainer = None
        try:
            dataset_path = os.path.normpath(os.path.join(_BASE_DIR, "..", "ml", "data", "demo_loan_data.csv"))
            reference = pd.read_csv(dataset_path)[FEATURE_COLUMNS].head(100)
            preprocessor = self._explain_pipeline.named_steps["preprocessor"]
            estimator = self._explain_pipeline.named_steps["classifier"]
            background = preprocessor.transform(reference)
            self._explainer = shap.Explainer(estimator, background)
            self._explanation_preprocessor = preprocessor
            self._explanation_feature_names = list(preprocessor.get_feature_names_out())
        except Exception:
            # Prediction remains available if a model type lacks a compatible SHAP explainer.
            self._explainer = None

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
            "artifact_sha256": self.artifact_sha256,
            "feature_schema_version": self.metadata.get("feature_schema_version", "v1.0"),
            "calibration": self.metadata.get("calibration", {"status": "NOT_CALIBRATED"}),
            "notice": self.metadata.get("notice"),
        }

    @staticmethod
    def classify_risk(default_probability: float) -> str:
        if default_probability < RISK_THRESHOLDS["LOW_MAX"]:
            return "LOW"
        elif default_probability < RISK_THRESHOLDS["MEDIUM_MAX"]:
            return "MEDIUM"
        return "HIGH"

    def _local_shap_explanation(self, row: pd.DataFrame) -> dict:
        if self._explainer is None:
            return {"status": "UNAVAILABLE", "method": "SHAP", "contributors": []}
        transformed = self._explanation_preprocessor.transform(row)
        explanation = self._explainer(transformed)
        values = explanation.values
        if getattr(values, "ndim", 0) == 3:
            # Class 1 is the default outcome.
            values = values[0, :, 1]
        else:
            values = values[0]
        grouped: dict[str, float] = {}
        for encoded_name, impact in zip(self._explanation_feature_names, values):
            raw_name = encoded_name.split("__", 1)[-1]
            source = next((feature for feature in FEATURE_COLUMNS if raw_name == feature or raw_name.startswith(feature + "_")), raw_name)
            grouped[source] = grouped.get(source, 0.0) + float(impact)
        ordered = sorted(grouped.items(), key=lambda item: abs(item[1]), reverse=True)[:8]
        return {
            "status": "AVAILABLE",
            "method": "SHAP",
            "target": "base estimator output (pre-calibration); not calibrated probability points",
            "base_value": float(explanation.base_values[0][1] if getattr(explanation.base_values, "ndim", 0) == 2 else explanation.base_values[0]),
            "contributors": [{"feature": self._humanize(name), "feature_key": name, "impact": round(value, 6)} for name, value in ordered],
        }

    def predict(self, features: dict) -> dict:
        with self._lock:
            row = pd.DataFrame([{col: features.get(col) for col in FEATURE_COLUMNS}])
            proba = self.pipeline.predict_proba(row)[0]
            local_explanation = self._local_shap_explanation(row)

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
            "model_hash": self.artifact_sha256,
            "feature_schema_version": self.metadata.get("feature_schema_version", "v1.0"),
            "credit_score": int(round((1.0 - default_probability) * 1000)),
            "credit_score_method": "round((1 - sigmoid-calibrated synthetic-model PD) × 1000)",
            "credit_score_validity": "Calibrated on held-out synthetic data only; not a validated consumer credit score.",
            "expected_loss": round(default_probability * settings.LOSS_GIVEN_DEFAULT * float(features["loan_amount"]), 2),
            "expected_loss_assumptions": {
                "loss_given_default": settings.LOSS_GIVEN_DEFAULT,
                "exposure_at_default": float(features["loan_amount"]),
                "formula": "PD × LGD × EAD",
                "status": "DEMO_ASSUMPTION_NOT_VALIDATED",
            },
            "risk_factors": risk_factors,
            "explanation_scope": "risk_factors are global model importance, not a local explanation; see local_explanation for SHAP values.",
            "local_explanation": local_explanation,
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
