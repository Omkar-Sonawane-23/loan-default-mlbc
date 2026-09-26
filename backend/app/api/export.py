from fastapi import APIRouter, Depends
from fastapi.responses import Response, JSONResponse

from app.dependencies import get_database
from app.services.export_service import ExportService

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/applications")
def export_applications(format: str = "csv", db=Depends(get_database)):
    service = ExportService(db)
    if format == "json":
        content = service.export_json()
        return Response(
            content=content, media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=applications.json"},
        )
    content = service.export_csv()
    return Response(
        content=content, media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=applications.csv"},
    )


@router.get("/applications/{application_id}/pdf")
def export_application_pdf(application_id: str, db=Depends(get_database)):
    service = ExportService(db)
    pdf_bytes = service.export_application_pdf(application_id)
    return Response(
        content=pdf_bytes, media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={application_id}.pdf"},
    )
