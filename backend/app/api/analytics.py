from fastapi import APIRouter, Depends
from app.dependencies import get_database
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("")
def get_analytics(db=Depends(get_database)):
    service = AnalyticsService(db)
    return service.full_analytics()
