"""application_service.py - business logic tying ML, MongoDB, and audit logging together."""
from fastapi import HTTPException

from app.repositories.application_repository import ApplicationRepository
from app.repositories.audit_repository import AuditRepository
from app.services.ml_service import get_ml_service


class ApplicationService:
    def __init__(self, db):
        self.repo = ApplicationRepository(db)
        self.audit_repo = AuditRepository(db)

    def create_application(self, payload: dict) -> dict:
        input_features = payload["input_features"]

        # If prediction fields are not already supplied, run real inference now.
        if payload.get("default_probability") is None:
            ml = get_ml_service()
            result = ml.predict(input_features)
            payload.update({
                "prediction": result["prediction"],
                "default_probability": result["default_probability"],
                "non_default_probability": result["non_default_probability"],
                "risk_category": result["risk_category"],
                "model_name": result["model_name"],
                "model_version": result["model_version"],
            })
            event = "Risk Prediction Generated"
            if payload.get("status") in (None, "DRAFT"):
                payload["status"] = "ASSESSED"
        else:
            event = "Application Created"

        payload.setdefault("status", "ASSESSED" if payload.get("default_probability") is not None else "DRAFT")

        application = self.repo.create(payload)
        self.audit_repo.add(application["application_id"], "Application Created", {
            "risk_category": application.get("risk_category"),
            "status": application.get("status"),
        })
        if event == "Risk Prediction Generated":
            self.audit_repo.add(application["application_id"], event, {
                "default_probability": application.get("default_probability"),
                "risk_category": application.get("risk_category"),
            })
        return application

    def get_application(self, application_id: str) -> dict:
        app = self.repo.get_by_id(application_id)
        if not app:
            raise HTTPException(status_code=404, detail=f"Application {application_id} not found")
        return app

    def update_application(self, application_id: str, updates: dict) -> dict:
        existing = self.get_application(application_id)
        clean_updates = {k: v for k, v in updates.items() if v is not None}

        # Re-run prediction if input features changed
        if "input_features" in clean_updates:
            ml = get_ml_service()
            result = ml.predict(clean_updates["input_features"])
            clean_updates.update({
                "prediction": result["prediction"],
                "default_probability": result["default_probability"],
                "non_default_probability": result["non_default_probability"],
                "risk_category": result["risk_category"],
                "model_name": result["model_name"],
                "model_version": result["model_version"],
            })

        updated = self.repo.update(application_id, clean_updates)
        self.audit_repo.add(application_id, "Application Updated", {
            "changed_fields": list(clean_updates.keys())
        })
        return updated

    def update_status(self, application_id: str, new_status: str) -> dict:
        existing = self.get_application(application_id)
        old_status = existing.get("status")
        updated = self.repo.update(application_id, {"status": new_status})
        self.audit_repo.add(application_id, "Status Changed", {
            "from": old_status, "to": new_status,
        })
        return updated

    def delete_application(self, application_id: str) -> dict:
        existing = self.get_application(application_id)
        was_registered = existing.get("blockchain", {}).get("registered", False)
        self.repo.delete(application_id)
        return {
            "deleted": True,
            "application_id": application_id,
            "blockchain_note": (
                "This application had a blockchain-registered record. Deleting it from "
                "MongoDB does NOT remove or alter its immutable history on the blockchain."
                if was_registered else None
            ),
        }

    def list_applications(self, **kwargs) -> tuple[list[dict], int]:
        return self.repo.list(**kwargs)

    def get_audit_log(self, application_id: str) -> list[dict]:
        self.get_application(application_id)  # 404 if missing
        return self.audit_repo.list_for_application(application_id)
