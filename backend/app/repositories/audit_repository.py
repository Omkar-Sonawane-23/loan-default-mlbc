"""audit_repository.py - MongoDB access for the audit_logs collection."""
import datetime
from pymongo import DESCENDING


class AuditRepository:
    def __init__(self, db):
        self.collection = db.audit_logs

    def add(self, application_id: str, event: str, details: dict = None) -> dict:
        entry = {
            "application_id": application_id,
            "event": event,
            "details": details or {},
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        self.collection.insert_one(entry)
        entry.pop("_id", None)
        return entry

    def list_for_application(self, application_id: str) -> list[dict]:
        cursor = self.collection.find(
            {"application_id": application_id}, {"_id": 0}
        ).sort("timestamp", DESCENDING)
        return list(cursor)

    def recent(self, limit: int = 20) -> list[dict]:
        cursor = self.collection.find({}, {"_id": 0}).sort("timestamp", DESCENDING).limit(limit)
        return list(cursor)
