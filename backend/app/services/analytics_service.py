"""analytics_service.py - real MongoDB aggregations for dashboard stats and analytics pages.

No statistic here is hardcoded -- every number is computed from the
applications currently stored in MongoDB.
"""
from collections import defaultdict


class AnalyticsService:
    def __init__(self, db):
        self.applications = db.applications
        self.blockchain_records = db.blockchain_records

    def dashboard_stats(self) -> dict:
        docs = list(self.applications.find({}, {"_id": 0}))
        total = len(docs)
        total_loan_amount = sum(d.get("input_features", {}).get("loan_amount", 0) for d in docs)
        low = sum(1 for d in docs if d.get("risk_category") == "LOW")
        medium = sum(1 for d in docs if d.get("risk_category") == "MEDIUM")
        high = sum(1 for d in docs if d.get("risk_category") == "HIGH")
        probs = [d.get("default_probability") for d in docs if d.get("default_probability") is not None]
        avg_prob = round(sum(probs) / len(probs), 4) if probs else 0.0
        registered = sum(1 for d in docs if d.get("blockchain", {}).get("registered"))
        verified = sum(1 for d in docs if d.get("status") == "VERIFIED")

        return {
            "total_applications": total,
            "total_loan_amount": round(total_loan_amount, 2),
            "low_risk": low,
            "medium_risk": medium,
            "high_risk": high,
            "average_default_probability": avg_prob,
            "blockchain_registered": registered,
            "verified_records": verified,
        }

    def recent_applications(self, limit: int = 5) -> list[dict]:
        cursor = self.applications.find({}, {"_id": 0, "_seq": 0}).sort("created_at", -1).limit(limit)
        return list(cursor)

    def high_risk_applications(self, limit: int = 5) -> list[dict]:
        cursor = self.applications.find(
            {"risk_category": "HIGH"}, {"_id": 0, "_seq": 0}
        ).sort("default_probability", -1).limit(limit)
        return list(cursor)

    def recent_blockchain_activity(self, limit: int = 5) -> list[dict]:
        cursor = self.blockchain_records.find({}, {"_id": 0}).sort("registered_at", -1).limit(limit)
        return list(cursor)

    def risk_distribution(self) -> dict:
        docs = list(self.applications.find({}, {"risk_category": 1}))
        counts = defaultdict(int)
        for d in docs:
            counts[d.get("risk_category", "UNKNOWN")] += 1
        return dict(counts)

    def applications_over_time(self) -> list[dict]:
        docs = list(self.applications.find({}, {"created_at": 1}))
        by_date = defaultdict(int)
        for d in docs:
            date_str = (d.get("created_at") or "")[:10]
            if date_str:
                by_date[date_str] += 1
        return [{"date": k, "count": v} for k, v in sorted(by_date.items())]

    def default_probability_distribution(self, bucket_size: float = 0.1) -> list[dict]:
        docs = list(self.applications.find({}, {"default_probability": 1}))
        buckets = defaultdict(int)
        for d in docs:
            p = d.get("default_probability")
            if p is None:
                continue
            bucket = min(int(p / bucket_size), 9)
            label = f"{bucket * int(bucket_size * 100)}-{(bucket + 1) * int(bucket_size * 100)}%"
            buckets[label] += 1
        return [{"range": k, "count": v} for k, v in sorted(buckets.items())]

    def loan_amount_by_risk(self) -> list[dict]:
        docs = list(self.applications.find({}, {"risk_category": 1, "input_features.loan_amount": 1}))
        sums = defaultdict(list)
        for d in docs:
            risk = d.get("risk_category", "UNKNOWN")
            amount = d.get("input_features", {}).get("loan_amount", 0)
            sums[risk].append(amount)
        return [
            {"risk_category": k, "average_loan_amount": round(sum(v) / len(v), 2) if v else 0, "count": len(v)}
            for k, v in sums.items()
        ]

    def credit_score_by_risk(self) -> list[dict]:
        docs = list(self.applications.find({}, {"risk_category": 1, "input_features.credit_score": 1}))
        sums = defaultdict(list)
        for d in docs:
            risk = d.get("risk_category", "UNKNOWN")
            score = d.get("input_features", {}).get("credit_score", 0)
            sums[risk].append(score)
        return [
            {"risk_category": k, "average_credit_score": round(sum(v) / len(v), 1) if v else 0}
            for k, v in sums.items()
        ]

    def employment_type_distribution(self) -> list[dict]:
        docs = list(self.applications.find({}, {"input_features.employment_type": 1}))
        counts = defaultdict(int)
        for d in docs:
            emp = d.get("input_features", {}).get("employment_type", "Unknown")
            counts[emp] += 1
        return [{"employment_type": k, "count": v} for k, v in counts.items()]

    def loan_purpose_distribution(self) -> list[dict]:
        docs = list(self.applications.find({}, {"input_features.requested_loan_purpose": 1}))
        counts = defaultdict(int)
        for d in docs:
            purpose = d.get("input_features", {}).get("requested_loan_purpose", "Unknown")
            counts[purpose] += 1
        return [{"loan_purpose": k, "count": v} for k, v in counts.items()]

    def blockchain_percentages(self) -> dict:
        total = self.applications.count_documents({})
        registered = self.applications.count_documents({"blockchain.registered": True})
        verified = self.applications.count_documents({"status": "VERIFIED"})
        return {
            "registration_percentage": round((registered / total) * 100, 1) if total else 0.0,
            "verification_percentage": round((verified / total) * 100, 1) if total else 0.0,
        }

    def full_analytics(self) -> dict:
        return {
            "risk_distribution": self.risk_distribution(),
            "applications_over_time": self.applications_over_time(),
            "default_probability_distribution": self.default_probability_distribution(),
            "loan_amount_by_risk": self.loan_amount_by_risk(),
            "credit_score_by_risk": self.credit_score_by_risk(),
            "employment_type_distribution": self.employment_type_distribution(),
            "loan_purpose_distribution": self.loan_purpose_distribution(),
            "blockchain": self.blockchain_percentages(),
        }
