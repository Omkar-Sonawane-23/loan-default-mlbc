from fastapi import APIRouter, Depends
from app.dependencies import get_database
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
def dashboard_stats(db=Depends(get_database)):
    service = AnalyticsService(db)
    return {
        "stats": service.dashboard_stats(),
        "recent_applications": service.recent_applications(limit=5),
        "recent_blockchain_activity": service.recent_blockchain_activity(limit=5),
        "high_risk_applications": service.high_risk_applications(limit=5),
        "charts": {
            "risk_distribution": service.risk_distribution(),
            "applications_over_time": service.applications_over_time(),
            "default_probability_distribution": service.default_probability_distribution(),
            "loan_amount_by_risk": service.loan_amount_by_risk(),
            "employment_type_distribution": service.employment_type_distribution(),
            "loan_purpose_distribution": service.loan_purpose_distribution(),
        },
    }
