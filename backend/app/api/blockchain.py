from fastapi import APIRouter, Depends
from app.dependencies import get_database
from app.services.blockchain_business_service import BlockchainBusinessService
from app.services.blockchain_service import get_blockchain_service, BlockchainNotConfiguredError
from app.repositories.blockchain_repository import BlockchainRepository
from fastapi import HTTPException

router = APIRouter(prefix="/blockchain", tags=["blockchain"])


@router.post("/register/{application_id}")
def register_on_blockchain(application_id: str, db=Depends(get_database)):
    service = BlockchainBusinessService(db)
    return service.register(application_id)


@router.get("/record/{application_id}")
def get_blockchain_record(application_id: str, db=Depends(get_database)):
    service = BlockchainBusinessService(db)
    return service.get_chain_record(application_id)


@router.get("/verify/{application_id}")
def verify_blockchain_record(application_id: str, db=Depends(get_database)):
    service = BlockchainBusinessService(db)
    return service.verify(application_id)


@router.get("/status")
def blockchain_network_status():
    try:
        chain = get_blockchain_service()
        available = chain.is_available()
        return {
            "available": available,
            "rpc_url": chain.w3.provider.endpoint_uri if hasattr(chain.w3.provider, "endpoint_uri") else None,
            "chain_id": chain.chain_id,
            "contract_address": chain.contract_address or None,
            "total_records_on_chain": chain.total_records() if available else None,
        }
    except Exception as e:
        return {"available": False, "error": str(e)}


@router.get("/transactions")
def recent_transactions(db=Depends(get_database)):
    repo = BlockchainRepository(db)
    return {"transactions": repo.recent(limit=20), "total_registered": repo.count()}
