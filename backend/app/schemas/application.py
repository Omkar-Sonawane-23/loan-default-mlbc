from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.prediction import LoanFeaturesInput

ApplicationStatus = Literal["DRAFT", "ASSESSED", "UNDER_REVIEW", "VERIFIED", "CLOSED"]
RiskCategory = Literal["LOW", "MEDIUM", "HIGH"]


class BlockchainInfo(BaseModel):
    registered: bool = False
    record_hash: Optional[str] = None
    transaction_hash: Optional[str] = None
    block_number: Optional[int] = None
    contract_address: Optional[str] = None
    chain_id: Optional[int] = None
    registered_at: Optional[str] = None


class ApplicationCreate(BaseModel):
    input_features: LoanFeaturesInput
    applicant_reference: Optional[str] = Field(None, max_length=64)
    prediction: Optional[int] = None
    default_probability: Optional[float] = None
    non_default_probability: Optional[float] = None
    risk_category: Optional[RiskCategory] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    status: ApplicationStatus = "DRAFT"


class ApplicationUpdate(BaseModel):
    input_features: Optional[LoanFeaturesInput] = None
    applicant_reference: Optional[str] = None
    status: Optional[ApplicationStatus] = None


class StatusUpdate(BaseModel):
    status: ApplicationStatus


class ApplicationOut(BaseModel):
    application_id: str
    applicant_reference: str
    input_features: dict
    prediction: Optional[int] = None
    default_probability: Optional[float] = None
    non_default_probability: Optional[float] = None
    risk_category: Optional[str] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    status: str
    created_at: str
    updated_at: str
    blockchain: BlockchainInfo


class PaginatedApplications(BaseModel):
    items: list[ApplicationOut]
    total: int
    page: int
    page_size: int
    total_pages: int


class AuditLogEntry(BaseModel):
    application_id: str
    event: str
    details: dict = {}
    timestamp: str
