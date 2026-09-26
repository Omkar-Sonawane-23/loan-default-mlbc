"""audit_service.py - convenience wrapper around AuditRepository for dashboard/recent-activity use."""
from app.repositories.audit_repository import AuditRepository


class AuditService:
    def __init__(self, db):
        self.repo = AuditRepository(db)

    def log(self, application_id: str, event: str, details: dict = None) -> dict:
        return self.repo.add(application_id, event, details)

    def recent_activity(self, limit: int = 20) -> list[dict]:
        return self.repo.recent(limit)

    def for_application(self, application_id: str) -> list[dict]:
        return self.repo.list_for_application(application_id)
