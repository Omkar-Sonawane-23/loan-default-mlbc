# Database Schema

Database: `loan_default_mlbc` (MongoDB)

## `applications`

```json
{
  "application_id": "LN-000001",
  "applicant_reference": "APP-000001",
  "input_features": {
    "age": 34, "annual_income": 720000, "employment_years": 6,
    "employment_type": "Salaried", "credit_score": 710, "loan_amount": 500000,
    "loan_term_months": 60, "existing_debt": 120000, "debt_to_income_ratio": 0.35,
    "number_of_previous_loans": 1, "previous_default": 0, "dependents": 1,
    "savings_amount": 200000, "requested_loan_purpose": "Home"
  },
  "prediction": 0,
  "default_probability": 0.0352,
  "non_default_probability": 0.9648,
  "risk_category": "LOW",
  "model_name": "Logistic Regression",
  "model_version": "v1-logistic-regression",
  "status": "ASSESSED",
  "created_at": "2026-01-01T00:00:00+00:00",
  "updated_at": "2026-01-01T00:00:00+00:00",
  "blockchain": {
    "registered": false,
    "record_hash": null,
    "transaction_hash": null,
    "block_number": null,
    "contract_address": null,
    "chain_id": null,
    "registered_at": null
  }
}
```

Indexes: unique on `application_id`; plus `applicant_reference`, `status`,
`risk_category`, `created_at` (descending), `blockchain.registered`, and a
text index across `application_id`, `applicant_reference`,
`input_features.requested_loan_purpose` for search.

## `audit_logs`

```json
{
  "application_id": "LN-000001",
  "event": "Blockchain Registered",
  "details": { "transaction_hash": "0x...", "block_number": 5 },
  "timestamp": "2026-01-01T00:05:00+00:00"
}
```

Events: `Application Created, Risk Prediction Generated, Application
Updated, Status Changed, Blockchain Registered, Blockchain Verified,
Record Verification Failed`.

## `blockchain_records`

A queryable mirror of each application's blockchain info (used for the
Blockchain page's recent-transactions list without scanning the full
`applications` collection).

```json
{
  "application_id": "LN-000001",
  "risk_category": "LOW",
  "registered": true,
  "record_hash": "0x...",
  "transaction_hash": "0x...",
  "block_number": 5,
  "contract_address": "0x...",
  "chain_id": 31337,
  "registered_at": "2026-01-01T00:05:00Z"
}
```

## `model_metadata`

Optionally mirrors `ml/models/model_metadata.json` into MongoDB for
querying model history over time (the backend reads the JSON file
directly by default; this collection exists for future extension, e.g.
tracking multiple trained model versions).
