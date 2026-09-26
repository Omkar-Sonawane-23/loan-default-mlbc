"""
seed_demo_applications.py

Generates a set of realistic demo LOAN APPLICATION records (not just raw
training rows) by running them through the actual trained model. The output
JSON is consumed by backend/scripts style seeding (see
backend/app/utils/seed.py) to populate MongoDB with a representative mix of:

  - LOW / MEDIUM / HIGH risk applications
  - different loan purposes, employment types, loan amounts
  - a mix of application statuses
  - some applications flagged as blockchain-registered (for UI demo only --
    actual on-chain registration still happens through the real
    /api/blockchain/register endpoint, this script only marks a subset as
    "should_register" so the operator can register them for a realistic demo)

This does NOT hardcode frontend mock data -- it produces a JSON seed file
generated from the real trained model's real predictions.
"""
import os
import sys
import json
import random
import datetime
import uuid

sys.path.insert(0, os.path.dirname(__file__) + "/../src")
from predict import LoanRiskModel

random.seed(42)

EMPLOYMENT_TYPES = ["Salaried", "Self-Employed", "Business Owner", "Contract", "Unemployed"]
LOAN_PURPOSES = ["Home", "Education", "Vehicle", "Personal", "Medical", "Business", "Debt Consolidation"]
STATUSES = ["DRAFT", "ASSESSED", "UNDER_REVIEW", "VERIFIED", "CLOSED"]

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "seed_applications.json")

N_SEED = 40


def random_application_features(i: int) -> dict:
    employment_type = random.choice(EMPLOYMENT_TYPES)
    age = random.randint(22, 62)
    return {
        "age": age,
        "annual_income": round(random.uniform(150000, 2200000), 2),
        "employment_years": round(min(random.uniform(0, 30), age - 21), 1),
        "employment_type": employment_type,
        "credit_score": random.randint(340, 890),
        "loan_amount": round(random.uniform(50000, 3000000), 2),
        "loan_term_months": random.choice([12, 24, 36, 48, 60, 84, 120, 180, 240]),
        "existing_debt": round(random.uniform(0, 900000), 2),
        "debt_to_income_ratio": round(random.uniform(0.02, 1.8), 3),
        "number_of_previous_loans": random.randint(0, 6),
        "previous_default": random.choice([0, 0, 0, 1]),
        "dependents": random.randint(0, 4),
        "savings_amount": round(random.uniform(0, 800000), 2),
        "requested_loan_purpose": random.choice(LOAN_PURPOSES),
    }


def main():
    model = LoanRiskModel()
    applications = []
    now = datetime.datetime.now(datetime.timezone.utc)

    for i in range(1, N_SEED + 1):
        features = random_application_features(i)
        result = model.predict(features)

        created_offset_days = random.randint(0, 120)
        created_at = now - datetime.timedelta(days=created_offset_days)

        status = random.choice(STATUSES)
        should_register = random.random() < 0.5  # ~50% flagged for demo blockchain registration

        application = {
            "application_id": f"LN-{i:06d}",
            "applicant_reference": f"APP-{i:06d}",
            "input_features": features,
            "prediction": 1 if result["default_probability"] >= 0.5 else 0,
            "default_probability": result["default_probability"],
            "non_default_probability": result["non_default_probability"],
            "risk_category": result["risk_category"],
            "model_name": result["model_name"],
            "model_version": result["model_version"],
            "status": status,
            "created_at": created_at.isoformat(),
            "updated_at": created_at.isoformat(),
            "should_register_demo": should_register,
            "blockchain": {
                "registered": False,
                "record_hash": None,
                "transaction_hash": None,
                "block_number": None,
                "contract_address": None,
                "chain_id": None,
                "registered_at": None,
            },
        }
        applications.append(application)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(applications, f, indent=2)

    risk_counts = {}
    for a in applications:
        risk_counts[a["risk_category"]] = risk_counts.get(a["risk_category"], 0) + 1

    print(f"Generated {len(applications)} seed applications -> {OUTPUT_PATH}")
    print(f"Risk distribution: {risk_counts}")


if __name__ == "__main__":
    main()
