"""blockchain_repository.py - MongoDB access for the blockchain_records collection.

This collection is a secondary, queryable ledger of blockchain registrations
(mirroring what's embedded in each application's `blockchain` field), used
for the /blockchain page's "recent transactions" list and dashboard stats.
"""
from pymongo import DESCENDING


class BlockchainRepository:
    def __init__(self, db):
        self.collection = db.blockchain_records

    def record(self, application_id: str, risk_category: str, chain_info: dict) -> dict:
        doc = {
            "application_id": application_id,
            "risk_category": risk_category,
            **chain_info,
        }
        self.collection.update_one(
            {"application_id": application_id}, {"$set": doc}, upsert=True
        )
        doc.pop("_id", None)
        return doc

    def recent(self, limit: int = 20) -> list[dict]:
        cursor = self.collection.find({}, {"_id": 0}).sort("registered_at", DESCENDING).limit(limit)
        return list(cursor)

    def count(self) -> int:
        return self.collection.count_documents({})

    def all(self) -> list[dict]:
        return list(self.collection.find({}, {"_id": 0}))
