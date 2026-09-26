"""
generate_demo_data.py

Generates a SYNTHETIC demo dataset for the LoanDefault MLBC academic project.

IMPORTANT: This dataset is entirely synthetic and generated for academic
demonstration purposes only. It does NOT represent real applicants, real
loans, or real financial institutions, and must never be used for actual
credit decisions.

The generation uses a fixed random seed (42) so that the dataset is
reproducible across runs.
"""

import numpy as np
import pandas as pd
import os

RANDOM_SEED = 42
N_RECORDS = 6000

EMPLOYMENT_TYPES = ["Salaried", "Self-Employed", "Business Owner", "Contract", "Unemployed"]
LOAN_PURPOSES = ["Home", "Education", "Vehicle", "Personal", "Medical", "Business", "Debt Consolidation"]

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "demo_loan_data.csv")


def generate_dataset(n_records: int = N_RECORDS, seed: int = RANDOM_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    age = rng.integers(21, 65, n_records)
    employment_type = rng.choice(EMPLOYMENT_TYPES, n_records, p=[0.45, 0.20, 0.12, 0.15, 0.08])

    # Income correlates loosely with employment type and age
    base_income = rng.normal(600000, 250000, n_records)
    employment_income_adj = np.select(
        [employment_type == "Unemployed", employment_type == "Business Owner"],
        [-350000, 150000],
        default=0,
    )
    annual_income = np.clip(base_income + employment_income_adj + (age - 21) * 3000, 90000, 5_000_000)

    employment_years = np.clip(
        rng.normal(np.clip((age - 21) * 0.4, 0, None), 3, n_records), 0, 40
    )
    employment_years = np.where(employment_type == "Unemployed", 0, employment_years)

    credit_score = np.clip(rng.normal(650, 90, n_records), 300, 900).round().astype(int)

    loan_amount = np.clip(rng.normal(800000, 500000, n_records), 20000, 8_000_000)
    loan_term_months = rng.choice([12, 24, 36, 48, 60, 84, 120, 180, 240], n_records)

    existing_debt = np.clip(rng.normal(200000, 180000, n_records), 0, 3_000_000)
    debt_to_income_ratio = np.clip((existing_debt + loan_amount * 0.08) / (annual_income + 1), 0, 3).round(3)

    number_of_previous_loans = rng.poisson(1.3, n_records)
    previous_default = rng.choice([0, 1], n_records, p=[0.85, 0.15])
    dependents = rng.integers(0, 5, n_records)
    savings_amount = np.clip(rng.exponential(150000, n_records), 0, 4_000_000)

    loan_purpose = rng.choice(LOAN_PURPOSES, n_records)

    # ---- Latent default-risk score (drives the synthetic target) ----
    risk_score = (
        -2.6
        - 0.013 * (credit_score - 650)
        + 1.7 * debt_to_income_ratio
        + 1.5 * previous_default
        - 0.05 * employment_years
        - 0.0000008 * annual_income
        + 0.0000004 * loan_amount
        + 0.10 * dependents
        - 0.0000010 * savings_amount
        + np.where(employment_type == "Unemployed", 1.3, 0)
        + np.where(employment_type == "Contract", 0.30, 0)
        + rng.normal(0, 0.6, n_records)  # noise
    )

    default_prob_latent = 1 / (1 + np.exp(-risk_score))
    loan_default = (rng.random(n_records) < default_prob_latent).astype(int)

    df = pd.DataFrame({
        "age": age,
        "annual_income": annual_income.round(2),
        "employment_years": employment_years.round(1),
        "employment_type": employment_type,
        "credit_score": credit_score,
        "loan_amount": loan_amount.round(2),
        "loan_term_months": loan_term_months,
        "existing_debt": existing_debt.round(2),
        "debt_to_income_ratio": debt_to_income_ratio,
        "number_of_previous_loans": number_of_previous_loans,
        "previous_default": previous_default,
        "dependents": dependents,
        "savings_amount": savings_amount.round(2),
        "requested_loan_purpose": loan_purpose,
        "loan_default": loan_default,
    })

    return df


if __name__ == "__main__":
    df = generate_dataset()
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Generated {len(df)} synthetic records -> {OUTPUT_PATH}")
    print(f"Default rate: {df['loan_default'].mean():.3%}")
    print(df.describe(include='all').T[['count', 'mean', 'std', 'min', 'max']].head(15))
