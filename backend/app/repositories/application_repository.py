"""application_repository.py - direct MongoDB access for the applications collection."""
from __future__ import annotations
import datetime
from typing import Optional

from pymongo import ASCENDING, DESCENDING


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class ApplicationRepository:
    def __init__(self, db):
        self.collection = db.applications

    def _next_application_id(self) -> str:
        last = self.collection.find_one(sort=[("_seq", DESCENDING)])
        next_seq = (last["_seq"] + 1) if last and "_seq" in last else 1
        return next_seq, f"LN-{next_seq:06d}"

    def create(self, doc: dict) -> dict:
        seq, application_id = self._next_application_id()
        now = _now_iso()
        doc["_seq"] = seq
        doc["application_id"] = application_id
        doc.setdefault("applicant_reference", f"APP-{seq:06d}")
        doc["created_at"] = now
        doc["updated_at"] = now
        doc.setdefault("blockchain", {
            "registered": False, "record_hash": None, "transaction_hash": None,
            "block_number": None, "contract_address": None, "chain_id": None,
            "registered_at": None,
        })
        self.collection.insert_one(doc)
        return self.get_by_id(application_id)

    def get_by_id(self, application_id: str) -> Optional[dict]:
        doc = self.collection.find_one({"application_id": application_id}, {"_id": 0, "_seq": 0})
        return doc

    def update(self, application_id: str, updates: dict) -> Optional[dict]:
        updates["updated_at"] = _now_iso()
        self.collection.update_one({"application_id": application_id}, {"$set": updates})
        return self.get_by_id(application_id)

    def delete(self, application_id: str) -> bool:
        result = self.collection.delete_one({"application_id": application_id})
        return result.deleted_count > 0

    def set_blockchain_info(self, application_id: str, blockchain_info: dict) -> Optional[dict]:
        return self.update(application_id, {"blockchain": blockchain_info})

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
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
    ) -> tuple[list[dict], int]:
        query: dict = {}

        if search:
            query["$or"] = [
                {"application_id": {"$regex": search, "$options": "i"}},
                {"applicant_reference": {"$regex": search, "$options": "i"}},
                {"input_features.requested_loan_purpose": {"$regex": search, "$options": "i"}},
            ]
        if risk_category:
            query["risk_category"] = risk_category
        if status:
            query["status"] = status
        if date_from or date_to:
            date_query = {}
            if date_from:
                date_query["$gte"] = date_from
            if date_to:
                date_query["$lte"] = date_to
            query["created_at"] = date_query
        if loan_amount_min is not None or loan_amount_max is not None:
            amount_query = {}
            if loan_amount_min is not None:
                amount_query["$gte"] = loan_amount_min
            if loan_amount_max is not None:
                amount_query["$lte"] = loan_amount_max
            query["input_features.loan_amount"] = amount_query
        if credit_score_min is not None or credit_score_max is not None:
            score_query = {}
            if credit_score_min is not None:
                score_query["$gte"] = credit_score_min
            if credit_score_max is not None:
                score_query["$lte"] = credit_score_max
            query["input_features.credit_score"] = score_query

        total = self.collection.count_documents(query)

        sort_direction = DESCENDING if sort_order == "desc" else ASCENDING
        skip = (page - 1) * page_size

        cursor = (
            self.collection.find(query, {"_id": 0, "_seq": 0})
            .sort(sort_by, sort_direction)
            .skip(skip)
            .limit(page_size)
        )
        items = list(cursor)
        return items, total

    def all(self) -> list[dict]:
        return list(self.collection.find({}, {"_id": 0, "_seq": 0}))

    def count(self) -> int:
        return self.collection.count_documents({})
