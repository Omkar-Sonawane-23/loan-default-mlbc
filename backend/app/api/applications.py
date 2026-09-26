import math
from typing import Optional
from fastapi import APIRouter, Depends, Query

from app.dependencies import get_database
from app.schemas.application import ApplicationCreate, ApplicationUpdate, StatusUpdate
from app.services.application_service import ApplicationService

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", status_code=201)
def create_application(payload: ApplicationCreate, db=Depends(get_database)):
    service = ApplicationService(db)
    data = payload.model_dump()
    data["input_features"] = data["input_features"]
    return service.create_application(data)


@router.get("")
def list_applications(
    db=Depends(get_database),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    risk_category: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    loan_amount_min: Optional[float] = None,
    loan_amount_max: Optional[float] = None,
    credit_score_min: Optional[int] = None,
    credit_score_max: Optional[int] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
):
    service = ApplicationService(db)
    items, total = service.list_applications(
        page=page, page_size=page_size, search=search, risk_category=risk_category,
        status=status, date_from=date_from, date_to=date_to,
        loan_amount_min=loan_amount_min, loan_amount_max=loan_amount_max,
        credit_score_min=credit_score_min, credit_score_max=credit_score_max,
        sort_by=sort_by, sort_order=sort_order,
    )
    total_pages = math.ceil(total / page_size) if total else 0
    return {
        "items": items, "total": total, "page": page,
        "page_size": page_size, "total_pages": total_pages,
    }


@router.get("/{application_id}")
def get_application(application_id: str, db=Depends(get_database)):
    service = ApplicationService(db)
    return service.get_application(application_id)


@router.put("/{application_id}")
def update_application(application_id: str, payload: ApplicationUpdate, db=Depends(get_database)):
    service = ApplicationService(db)
    updates = payload.model_dump(exclude_unset=True)
    if "input_features" in updates and updates["input_features"] is not None:
        pass  # already a dict via model_dump
    return service.update_application(application_id, updates)


@router.delete("/{application_id}")
def delete_application(application_id: str, db=Depends(get_database)):
    service = ApplicationService(db)
    return service.delete_application(application_id)


@router.patch("/{application_id}/status")
def update_status(application_id: str, payload: StatusUpdate, db=Depends(get_database)):
    service = ApplicationService(db)
    return service.update_status(application_id, payload.status)


@router.get("/{application_id}/audit")
def get_audit_log(application_id: str, db=Depends(get_database)):
    service = ApplicationService(db)
    return {"application_id": application_id, "events": service.get_audit_log(application_id)}
