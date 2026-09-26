"""
hashing_service.py

Produces a deterministic SHA-256 hash of the canonical, immutable portion
of a loan application record. The canonical representation:

  - includes only fields that determine the record's integrity
    (application_id, applicant_reference, input_features, prediction
    results, model info, status)
  - uses stable JSON serialization: sorted keys, fixed separators, UTF-8
  - is float-safe: numeric values are rounded to a fixed precision before
    serialization so that harmless floating point representation
    differences don't change the hash

The same application state ALWAYS produces the same hash. Any modification
to a canonical field produces a different hash. This is what powers
blockchain registration and later tamper-evidence verification.
"""
import hashlib
import json


CANONICAL_FIELDS = [
    "application_id",
    "applicant_reference",
    "input_features",
    "prediction",
    "default_probability",
    "non_default_probability",
    "risk_category",
    "model_name",
    "model_version",
    "status",
]


def _round_floats(obj):
    """Recursively round floats to 6 decimal places for stable hashing."""
    if isinstance(obj, float):
        return round(obj, 6)
    if isinstance(obj, dict):
        return {k: _round_floats(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_round_floats(v) for v in obj]
    return obj


def build_canonical_record(application: dict) -> dict:
    """Extract only the canonical, hash-relevant fields from an application."""
    canonical = {}
    for field in CANONICAL_FIELDS:
        canonical[field] = application.get(field)
    return _round_floats(canonical)


def canonical_json(application: dict) -> str:
    canonical = build_canonical_record(application)
    return json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_record_hash(application: dict) -> str:
    """Returns a '0x'-prefixed hex SHA-256 hash of the canonical record."""
    payload = canonical_json(application).encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    return "0x" + digest
