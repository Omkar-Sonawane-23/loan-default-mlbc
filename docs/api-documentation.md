# API Documentation

Base URL: `http://127.0.0.1:8000/api`

Interactive docs (Swagger UI): `http://127.0.0.1:8000/docs`

## Health & Model

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Backend, MongoDB, ML model, and blockchain status |
| GET | `/model/info` | Current model name, version, training date, features |
| GET | `/model/metrics` | Metrics, feature importance, full model comparison |

## Predictions

| Method | Path | Description |
|---|---|---|
| POST | `/predictions` | Run real-time ML inference on loan features (no persistence) |

## Applications

| Method | Path | Description |
|---|---|---|
| POST | `/applications` | Create an application (runs prediction if not supplied) |
| GET | `/applications` | List with pagination, search, filters, sorting |
| GET | `/applications/{id}` | Get one application |
| PUT | `/applications/{id}` | Update (re-runs prediction if features changed) |
| DELETE | `/applications/{id}` | Delete from MongoDB (does not affect on-chain history) |
| PATCH | `/applications/{id}/status` | Update status |
| GET | `/applications/{id}/audit` | Full audit timeline |

### List query parameters
`page, page_size, search, risk_category, status, date_from, date_to,
loan_amount_min, loan_amount_max, credit_score_min, credit_score_max,
sort_by, sort_order`

## Dashboard & Analytics

| Method | Path | Description |
|---|---|---|
| GET | `/dashboard/stats` | Stats, recent applications, recent blockchain activity, charts |
| GET | `/analytics` | Full analytics: distributions, trends, blockchain rates |

## Blockchain

| Method | Path | Description |
|---|---|---|
| POST | `/blockchain/register/{id}` | Register application's hash on-chain (real transaction) |
| GET | `/blockchain/record/{id}` | Read the raw on-chain record |
| GET | `/blockchain/verify/{id}` | Compare current DB hash vs on-chain hash |
| GET | `/blockchain/status` | Network/contract status |
| GET | `/blockchain/transactions` | Recent on-chain registrations |

## Export

| Method | Path | Description |
|---|---|---|
| GET | `/export/applications?format=csv\|json` | Export all applications |
| GET | `/export/applications/{id}/pdf` | Per-application PDF report |

## Error format

```json
{ "detail": "Human-readable error message" }
```

Standard HTTP status codes are used: `404` (not found), `409` (conflict,
e.g. duplicate blockchain registration), `422` (validation error), `502`
(blockchain transaction failed), `503` (blockchain/model not configured).
