"""
blockchain_business_service.py

The application-level blockchain workflow: register an application's
canonical hash on-chain, and later verify it. This is distinct from
blockchain_service.py, which is the low-level web3.py wrapper.
"""
from fastapi import HTTPException

from app.repositories.application_repository import ApplicationRepository
from app.repositories.audit_repository import AuditRepository
from app.repositories.blockchain_repository import BlockchainRepository
from app.services.blockchain_service import get_blockchain_service, BlockchainNotConfiguredError
from app.services.hashing_service import compute_record_hash


class BlockchainBusinessService:
    def __init__(self, db):
        self.app_repo = ApplicationRepository(db)
        self.audit_repo = AuditRepository(db)
        self.chain_repo = BlockchainRepository(db)

    def register(self, application_id: str) -> dict:
        application = self.app_repo.get_by_id(application_id)
        if not application:
            raise HTTPException(status_code=404, detail=f"Application {application_id} not found")

        if application.get("blockchain", {}).get("registered"):
            raise HTTPException(
                status_code=409,
                detail=f"Application {application_id} is already registered on the blockchain."
            )
        if application.get("risk_category") is None:
            raise HTTPException(
                status_code=400,
                detail="Application must have a risk prediction before blockchain registration."
            )

        record_hash = compute_record_hash(application)

        chain = get_blockchain_service()
        try:
            tx_result = chain.register_record(application_id, record_hash, application["risk_category"])
        except BlockchainNotConfiguredError as e:
            raise HTTPException(status_code=503, detail=str(e))
        except Exception as e:
            if "already registered" in str(e).lower() or chain.record_exists(application_id):
                raise HTTPException(
                    status_code=409,
                    detail=f"Application {application_id} is already registered on the blockchain."
                )
            raise HTTPException(status_code=502, detail=f"Blockchain transaction failed: {e}")

        blockchain_info = {
            "registered": True,
            "record_hash": record_hash,
            "transaction_hash": tx_result["transaction_hash"],
            "block_number": tx_result["block_number"],
            "contract_address": tx_result["contract_address"],
            "chain_id": tx_result["chain_id"],
            "registered_at": tx_result["registered_at"],
        }
        self.app_repo.set_blockchain_info(application_id, blockchain_info)
        self.chain_repo.record(application_id, application["risk_category"], blockchain_info)
        self.audit_repo.add(application_id, "Blockchain Registered", {
            "transaction_hash": tx_result["transaction_hash"],
            "block_number": tx_result["block_number"],
            "record_hash": record_hash,
        })

        return {
            "application_id": application_id,
            "record_hash": record_hash,
            "risk_category": application["risk_category"],
            **tx_result,
        }

    def get_chain_record(self, application_id: str) -> dict:
        application = self.app_repo.get_by_id(application_id)
        if not application:
            raise HTTPException(status_code=404, detail=f"Application {application_id} not found")

        chain = get_blockchain_service()
        try:
            record = chain.get_record(application_id)
        except BlockchainNotConfiguredError as e:
            raise HTTPException(status_code=503, detail=str(e))

        if record is None:
            raise HTTPException(status_code=404, detail="No on-chain record found for this application.")
        return record

    def verify(self, application_id: str) -> dict:
        application = self.app_repo.get_by_id(application_id)
        if not application:
            raise HTTPException(status_code=404, detail=f"Application {application_id} not found")

        current_hash = compute_record_hash(application)
        blockchain_info = application.get("blockchain", {})

        if not blockchain_info.get("registered"):
            return {
                "application_id": application_id,
                "verified": False,
                "current_database_hash": current_hash,
                "blockchain_hash": None,
                "transaction_hash": None,
                "block_number": None,
                "registered_at": None,
                "message": "This application has not been registered on the blockchain yet.",
            }

        chain = get_blockchain_service()
        try:
            on_chain_verified = chain.verify_record(application_id, current_hash)
            on_chain_record = chain.get_record(application_id)
        except BlockchainNotConfiguredError as e:
            raise HTTPException(status_code=503, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Blockchain read failed: {e}")

        event = "Blockchain Verified" if on_chain_verified else "Record Verification Failed"
        self.audit_repo.add(application_id, event, {
            "current_database_hash": current_hash,
            "blockchain_hash": on_chain_record["record_hash"] if on_chain_record else None,
        })

        return {
            "application_id": application_id,
            "verified": on_chain_verified,
            "current_database_hash": current_hash,
            "blockchain_hash": on_chain_record["record_hash"] if on_chain_record else None,
            "transaction_hash": blockchain_info.get("transaction_hash"),
            "block_number": blockchain_info.get("block_number"),
            "registered_at": blockchain_info.get("registered_at"),
            "message": (
                "VERIFIED: the database record matches the blockchain record. No tampering detected."
                if on_chain_verified else
                "VERIFICATION FAILED: the current database record does not match the hash stored "
                "on the blockchain. The record may have been modified after registration."
            ),
        }
