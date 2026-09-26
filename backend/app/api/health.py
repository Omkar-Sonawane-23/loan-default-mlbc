from fastapi import APIRouter
from app.database import database
from app.services.blockchain_service import get_blockchain_service
from app.services.ml_service import get_ml_service
from app.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    mongo_ok = database.is_connected() if database.client else False

    try:
        model_loaded = get_ml_service() is not None
    except Exception:
        model_loaded = False

    try:
        blockchain_ok = get_blockchain_service().is_available()
    except Exception:
        blockchain_ok = False

    return {
        "status": "ok" if mongo_ok else "degraded",
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "mongodb_connected": mongo_ok,
        "ml_model_loaded": model_loaded,
        "blockchain_available": blockchain_ok,
    }
