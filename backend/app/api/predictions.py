from datetime import datetime, timezone
import logging
from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_database
from app.schemas.prediction import PredictionRequest
from app.services.ml_service import get_ml_service

router = APIRouter(prefix="/predictions", tags=["predictions"])
logger = logging.getLogger(__name__)


@router.post("")
def create_prediction(payload: PredictionRequest, db=Depends(get_database)):
    try:
        ml = get_ml_service()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    features = payload.input_features.model_dump()
    result = ml.predict(features)
    # Operational prediction log stays off-chain; keep full features only in the private DB.
    result["storage_status"] = "NOT_CONFIGURED" if db is None else "PENDING"
    if db is not None:
        try:
            recorded_result = {**result, "storage_status": "STORED"}
            db.model_predictions.insert_one({
                "input_features": features,
                "prediction": recorded_result,
                "model_version": result["model_version"],
                "created_at": datetime.now(timezone.utc),
                "data_source": "user_provided",
            })
            result["storage_status"] = "STORED"
        except Exception as exc:
            # Inference can still run during a persistence outage, but never imply it was recorded.
            logger.warning("Prediction persistence unavailable (%s)", type(exc).__name__)
            result["storage_status"] = "UNAVAILABLE"
    return result
