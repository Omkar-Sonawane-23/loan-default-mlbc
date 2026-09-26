"""Inference helper used by both ML scripts and the FastAPI backend."""
import json
import os
import joblib
import pandas as pd

from config import MODEL_PATH, METADATA_PATH, FEATURE_COLUMNS, RISK_THRESHOLDS


class LoanRiskModel:
    """Wraps the trained pipeline for single/batch inference."""

    def __init__(self, model_path: str = MODEL_PATH, metadata_path: str = METADATA_PATH):
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found at {model_path}. Run ml/scripts/train_model.py first."
            )
        self.pipeline = joblib.load(model_path)
        with open(metadata_path) as f:
            self.metadata = json.load(f)

    @property
    def model_name(self) -> str:
        return self.metadata["model_name"]

    @property
    def model_version(self) -> str:
        return self.metadata["model_version"]

    @property
    def feature_importance(self):
        return self.metadata.get("feature_importance", [])

    @staticmethod
    def classify_risk(default_probability: float) -> str:
        if default_probability < RISK_THRESHOLDS["LOW_MAX"]:
            return "LOW"
        elif default_probability < RISK_THRESHOLDS["MEDIUM_MAX"]:
            return "MEDIUM"
        return "HIGH"

    def predict(self, features: dict) -> dict:
        """Run inference on a single application's feature dict."""
        row = pd.DataFrame([{col: features.get(col) for col in FEATURE_COLUMNS}])
        proba = self.pipeline.predict_proba(row)[0]
        default_probability = float(proba[1])
        non_default_probability = float(proba[0])
        risk_category = self.classify_risk(default_probability)

        return {
            "default_probability": round(default_probability, 4),
            "non_default_probability": round(non_default_probability, 4),
            "risk_category": risk_category,
            "model_name": self.model_name,
            "model_version": self.model_version,
        }


if __name__ == "__main__":
    model = LoanRiskModel()
    sample = {
        "age": 34, "annual_income": 720000, "employment_years": 6,
        "employment_type": "Salaried", "credit_score": 710, "loan_amount": 500000,
        "loan_term_months": 60, "existing_debt": 120000, "debt_to_income_ratio": 0.35,
        "number_of_previous_loans": 1, "previous_default": 0, "dependents": 1,
        "savings_amount": 200000, "requested_loan_purpose": "Home",
    }
    print(model.predict(sample))
