"""Shared constants used across the backend."""

APPLICATION_STATUSES = ["DRAFT", "ASSESSED", "UNDER_REVIEW", "VERIFIED", "CLOSED"]
RISK_CATEGORIES = ["LOW", "MEDIUM", "HIGH"]

AUDIT_EVENTS = [
    "Application Created",
    "Risk Prediction Generated",
    "Application Updated",
    "Status Changed",
    "Blockchain Registered",
    "Blockchain Verified",
    "Record Verification Failed",
]
