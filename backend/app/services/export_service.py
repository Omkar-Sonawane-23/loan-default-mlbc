"""export_service.py - CSV/JSON export of applications, and a per-application PDF report."""
import csv
import io
import json

from fastapi import HTTPException
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from app.repositories.application_repository import ApplicationRepository
from app.config import settings

CSV_COLUMNS = [
    "application_id", "applicant_reference", "status", "risk_category",
    "default_probability", "non_default_probability", "model_name", "model_version",
    "created_at", "updated_at",
]


class ExportService:
    def __init__(self, db):
        self.repo = ApplicationRepository(db)

    def export_csv(self) -> str:
        applications = self.repo.all()
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=CSV_COLUMNS + [
            "loan_amount", "credit_score", "employment_type", "requested_loan_purpose",
            "blockchain_registered", "transaction_hash",
        ])
        writer.writeheader()
        for app in applications:
            features = app.get("input_features", {})
            blockchain = app.get("blockchain", {})
            row = {k: app.get(k) for k in CSV_COLUMNS}
            row.update({
                "loan_amount": features.get("loan_amount"),
                "credit_score": features.get("credit_score"),
                "employment_type": features.get("employment_type"),
                "requested_loan_purpose": features.get("requested_loan_purpose"),
                "blockchain_registered": blockchain.get("registered"),
                "transaction_hash": blockchain.get("transaction_hash"),
            })
            writer.writerow(row)
        return buffer.getvalue()

    def export_json(self) -> str:
        applications = self.repo.all()
        return json.dumps(applications, indent=2, default=str)

    def export_application_pdf(self, application_id: str) -> bytes:
        app = self.repo.get_by_id(application_id)
        if not app:
            raise HTTPException(status_code=404, detail=f"Application {application_id} not found")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontSize=16)
        section_style = ParagraphStyle("SectionStyle", parent=styles["Heading2"], fontSize=12, spaceBefore=12)
        normal = styles["Normal"]

        elements = []
        elements.append(Paragraph("LoanDefault MLBC - Application Report", title_style))
        elements.append(Paragraph(f"Application ID: {app['application_id']}", normal))
        elements.append(Spacer(1, 10))

        features = app.get("input_features", {})
        blockchain = app.get("blockchain", {})

        def table_from_dict(d: dict) -> Table:
            data = [[k.replace("_", " ").title(), str(v)] for k, v in d.items()]
            t = Table(data, colWidths=[70 * mm, 90 * mm])
            t.setStyle(TableStyle([
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f3f4f6")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            return t

        elements.append(Paragraph("Loan &amp; Financial Details", section_style))
        elements.append(table_from_dict(features))

        elements.append(Paragraph("ML Prediction", section_style))
        elements.append(table_from_dict({
            "Default Probability": app.get("default_probability"),
            "Non-default Probability": app.get("non_default_probability"),
            "Risk Category": app.get("risk_category"),
            "Model": app.get("model_name"),
            "Model Version": app.get("model_version"),
            "Status": app.get("status"),
        }))

        elements.append(Paragraph("Blockchain Status", section_style))
        elements.append(table_from_dict({
            "Registered": blockchain.get("registered", False),
            "Record Hash": blockchain.get("record_hash") or "-",
            "Transaction Hash": blockchain.get("transaction_hash") or "-",
            "Block Number": blockchain.get("block_number") or "-",
            "Chain ID": blockchain.get("chain_id") or "-",
            "Registered At": blockchain.get("registered_at") or "-",
        }))

        elements.append(Spacer(1, 16))
        elements.append(Paragraph("Disclaimer", section_style))
        elements.append(Paragraph(settings.ACADEMIC_DISCLAIMER, normal))

        doc.build(elements)
        return buffer.getvalue()
