from typing import Optional
from pydantic import BaseModel


class BlockchainRegisterResponse(BaseModel):
    application_id: str
    record_hash: str
    transaction_hash: str
    block_number: int
    contract_address: str
    chain_id: int
    risk_category: str
    registered_at: str


class BlockchainRecordOut(BaseModel):
    application_id: str
    record_hash: str
    risk_category: str
    timestamp: int
    registrar: str


class BlockchainVerifyResponse(BaseModel):
    application_id: str
    verified: bool
    current_database_hash: str
    blockchain_hash: Optional[str] = None
    transaction_hash: Optional[str] = None
    block_number: Optional[int] = None
    registered_at: Optional[str] = None
    message: str
