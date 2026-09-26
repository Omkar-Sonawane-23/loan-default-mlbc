from app.services.hashing_service import compute_record_hash, build_canonical_record


SAMPLE_APPLICATION = {
    "application_id": "LN-000001",
    "applicant_reference": "APP-000001",
    "input_features": {"age": 34, "credit_score": 710, "loan_amount": 500000.0},
    "prediction": 0,
    "default_probability": 0.0352,
    "non_default_probability": 0.9648,
    "risk_category": "LOW",
    "model_name": "Logistic Regression",
    "model_version": "v1-logistic-regression",
    "status": "ASSESSED",
    "created_at": "2026-01-01T00:00:00Z",  # not part of canonical record
}


def test_hash_is_deterministic_for_same_record():
    hash1 = compute_record_hash(SAMPLE_APPLICATION)
    hash2 = compute_record_hash(dict(SAMPLE_APPLICATION))
    assert hash1 == hash2


def test_hash_changes_when_canonical_field_modified():
    original_hash = compute_record_hash(SAMPLE_APPLICATION)

    tampered = dict(SAMPLE_APPLICATION)
    tampered["risk_category"] = "HIGH"
    tampered_hash = compute_record_hash(tampered)

    assert original_hash != tampered_hash


def test_hash_unaffected_by_non_canonical_field_change():
    original_hash = compute_record_hash(SAMPLE_APPLICATION)

    modified = dict(SAMPLE_APPLICATION)
    modified["created_at"] = "2099-12-31T23:59:59Z"  # not in canonical field list
    modified_hash = compute_record_hash(modified)

    assert original_hash == modified_hash


def test_hash_is_sha256_hex_with_0x_prefix():
    h = compute_record_hash(SAMPLE_APPLICATION)
    assert h.startswith("0x")
    assert len(h) == 66  # 0x + 64 hex chars


def test_float_rounding_does_not_change_hash():
    a = dict(SAMPLE_APPLICATION)
    b = dict(SAMPLE_APPLICATION)
    a["default_probability"] = 0.03520001
    b["default_probability"] = 0.0352
    # both round to 0.0352 at 6 decimal places -> same hash
    assert compute_record_hash(a) == compute_record_hash(b)


def test_canonical_record_excludes_non_canonical_fields():
    canonical = build_canonical_record(SAMPLE_APPLICATION)
    assert "created_at" not in canonical
    assert canonical["application_id"] == "LN-000001"
