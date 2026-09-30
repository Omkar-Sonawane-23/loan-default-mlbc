"""Operational monitoring summary based on recorded inference events."""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from app.dependencies import get_database
from app.services.drift_service import drift_band, population_stability_index
from app.services.ml_service import get_ml_service

router = APIRouter(prefix="/model-monitoring", tags=["model monitoring"])


@router.get("/summary")
def monitoring_summary(db=Depends(get_database), window_days: int = 30):
    """Compare recent and preceding prediction windows (no labels required)."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=max(1, min(window_days, 365)))
    earlier_cutoff = cutoff - timedelta(days=max(1, min(window_days, 365)))
    base = db.model_predictions if db is not None else None
    db_available = base is not None
    try:
        recent = list(base.find({"created_at": {"$gte": cutoff}}).sort("created_at", 1)) if db_available else []
        prior = list(base.find({"created_at": {"$gte": earlier_cutoff, "$lt": cutoff}}).sort("created_at", 1)) if db_available else []
    except Exception:
        # Monitoring must report an honest unavailable state without leaking DB details.
        db_available = False
        recent, prior = [], []
    recent_pd = [float(row.get("prediction", {}).get("default_probability", 0)) for row in recent]
    prior_pd = [float(row.get("prediction", {}).get("default_probability", 0)) for row in prior]
    psi = population_stability_index(prior_pd, recent_pd)
    model = get_ml_service()
    return {
        "status": "OBSERVING" if recent and prior else ("INSUFFICIENT_DATA" if db_available else "DATABASE_UNAVAILABLE"),
        "model_version": model.model_version,
        "model_hash": model.artifact_sha256,
        "window_days": max(1, min(window_days, 365)),
        "recent_prediction_count": len(recent),
        "comparison_prediction_count": len(prior),
        "prediction_drift_psi": round(psi, 6) if psi is not None else None,
        "prediction_drift_band": drift_band(psi),
        "recent_mean_default_probability": round(sum(recent_pd) / len(recent_pd), 6) if recent_pd else None,
        "comparison_mean_default_probability": round(sum(prior_pd) / len(prior_pd), 6) if prior_pd else None,
        "feature_drift": "UNAVAILABLE: no production/reference feature monitoring baseline is configured",
        "label_performance": "PENDING: outcome labels are not collected by this monitoring endpoint",
        "interpretation": "PSI is a screening indicator, not a validated performance or fairness conclusion.",
    }
