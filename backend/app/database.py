"""MongoDB connection management using PyMongo."""
import logging
from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from pymongo.errors import PyMongoError

from app.config import settings

logger = logging.getLogger(__name__)


class Database:
    client: MongoClient = None
    db = None

    def connect(self):
        self.client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
        self.db = self.client[settings.MONGODB_DB]
        return self.db

    def close(self):
        if self.client:
            self.client.close()

    def is_connected(self) -> bool:
        try:
            self.client.admin.command("ping")
            return True
        except Exception:
            return False

    def ensure_indexes(self):
        """Create indexes required by the application. Safe to call repeatedly."""
        applications = self.db.applications
        applications.create_index([("application_id", ASCENDING)], unique=True)
        applications.create_index([("applicant_reference", ASCENDING)])
        applications.create_index([("status", ASCENDING)])
        applications.create_index([("risk_category", ASCENDING)])
        applications.create_index([("created_at", DESCENDING)])
        applications.create_index([("blockchain.registered", ASCENDING)])
        applications.create_index(
            [("application_id", TEXT), ("applicant_reference", TEXT), ("input_features.requested_loan_purpose", TEXT)]
        )

        audit_logs = self.db.audit_logs
        audit_logs.create_index([("application_id", ASCENDING)])
        audit_logs.create_index([("timestamp", DESCENDING)])

        blockchain_records = self.db.blockchain_records
        blockchain_records.create_index([("application_id", ASCENDING)], unique=True)
        blockchain_records.create_index([("transaction_hash", ASCENDING)])

        model_metadata = self.db.model_metadata
        model_metadata.create_index([("model_version", ASCENDING)])

        model_predictions = self.db.model_predictions
        model_predictions.create_index([("created_at", DESCENDING)])
        model_predictions.create_index([("model_version", ASCENDING), ("created_at", DESCENDING)])

        loan_lifecycle = self.db.loan_lifecycle
        loan_lifecycle.create_index([("loan_id", ASCENDING)], unique=True)
        loan_lifecycle.create_index([("contract_state", ASCENDING), ("updated_at", DESCENDING)])


database = Database()


def get_db():
    return database.db
