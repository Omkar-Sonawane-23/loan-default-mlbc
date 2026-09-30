from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator


class LoanFeaturesInput(BaseModel):
    age: int = Field(..., ge=18, le=100)
    annual_income: float = Field(..., ge=0)
    employment_years: float = Field(..., ge=0, le=80)
    employment_type: Literal["Salaried", "Self-Employed", "Business Owner", "Contract", "Unemployed"]
    credit_score: int = Field(..., ge=300, le=900)
    loan_amount: float = Field(..., gt=0)
    loan_term_months: int = Field(..., gt=0, le=480)
    existing_debt: float = Field(..., ge=0)
    debt_to_income_ratio: float = Field(..., ge=0, le=10)
    number_of_previous_loans: int = Field(..., ge=0)
    previous_default: Literal[0, 1]
    dependents: int = Field(..., ge=0, le=20)
    savings_amount: float = Field(..., ge=0)
    requested_loan_purpose: Literal[
        "Home", "Education", "Vehicle", "Personal", "Medical", "Business", "Debt Consolidation"
    ]

    @field_validator("annual_income", "loan_amount", "existing_debt", "savings_amount")
    @classmethod
    def must_be_finite(cls, v):
        if v != v or v in (float("inf"), float("-inf")):
            raise ValueError("must be a finite number")
        return v


class PredictionRequest(BaseModel):
    input_features: LoanFeaturesInput
    applicant_reference: Optional[str] = Field(None, max_length=64)


class PredictionResult(BaseModel):
    default_probability: float
    non_default_probability: float
    risk_category: Literal["LOW", "MEDIUM", "HIGH"]
    model_name: str
    model_version: str
    model_hash: str = ""
    feature_schema_version: str = "v1.0"
    credit_score: int = Field(..., ge=0, le=1000)
    credit_score_method: str = ""
    credit_score_validity: str = ""
    expected_loss: float = Field(..., ge=0)
    expected_loss_assumptions: dict = {}
    storage_status: str = "UNAVAILABLE"
    explanation_scope: str = ""
    local_explanation: dict = {}
    risk_factors: list[dict] = []
    disclaimer: str
