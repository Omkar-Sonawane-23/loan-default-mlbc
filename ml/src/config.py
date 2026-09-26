"""Shared configuration for the ML pipeline."""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(BASE_DIR, "data", "demo_loan_data.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

MODEL_PATH = os.path.join(MODEL_DIR, "loan_default_model.joblib")
METADATA_PATH = os.path.join(MODEL_DIR, "model_metadata.json")
METRICS_PATH = os.path.join(REPORTS_DIR, "model_metrics.json")
COMPARISON_PATH = os.path.join(REPORTS_DIR, "model_comparison.json")
CONFUSION_MATRIX_PATH = os.path.join(REPORTS_DIR, "confusion_matrix.png")
FEATURE_IMPORTANCE_PATH = os.path.join(REPORTS_DIR, "feature_importance.png")

TARGET_COLUMN = "loan_default"

NUMERIC_FEATURES = [
    "age",
    "annual_income",
    "employment_years",
    "credit_score",
    "loan_amount",
    "loan_term_months",
    "existing_debt",
    "debt_to_income_ratio",
    "number_of_previous_loans",
    "previous_default",
    "dependents",
    "savings_amount",
]

CATEGORICAL_FEATURES = [
    "employment_type",
    "requested_loan_purpose",
]

FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES

RANDOM_SEED = 42
TEST_SIZE = 0.2

# Demonstration-only risk thresholds (NOT financially validated)
RISK_THRESHOLDS = {
    "LOW_MAX": 0.30,
    "MEDIUM_MAX": 0.70,
}

MODEL_VERSION_PREFIX = "v1"
