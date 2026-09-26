from fastapi import APIRouter, HTTPException
from app.services.ml_service import get_ml_service

router = APIRouter(prefix="/model", tags=["model"])


@router.get("/info")
def model_info():
    try:
        ml = get_ml_service()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return ml.info


@router.get("/metrics")
def model_metrics():
    try:
        ml = get_ml_service()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return {
        "selected_model": ml.model_name,
        "model_version": ml.model_version,
        "metrics": ml.metrics,
        "feature_importance": ml.feature_importance,
        "model_comparison": ml.comparison,
    }
