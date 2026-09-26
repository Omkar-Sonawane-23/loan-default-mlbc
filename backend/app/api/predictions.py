from fastapi import APIRouter, HTTPException
from app.schemas.prediction import PredictionRequest
from app.services.ml_service import get_ml_service

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post("")
def create_prediction(payload: PredictionRequest):
    try:
        ml = get_ml_service()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    result = ml.predict(payload.input_features.model_dump())
    return result
