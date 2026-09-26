# Architecture

## System Overview

```
React Frontend (Vite, TS, Tailwind)
      |
      | REST API (axios)
      v
FastAPI Backend
      |
      +--------------------+
      |                    |
      v                    v
ML Service              MongoDB
(scikit-learn            (applications, audit_logs,
 pipeline, joblib)         model_metadata, blockchain_records)
      |
      v
Risk Prediction (default_probability, risk_category)

FastAPI Backend
      |
      | web3.py (HTTP JSON-RPC)
      v
Hardhat Local Blockchain (chain id 31337)
      |
      v
LoanRecordRegistry.sol
```

## Request flow: creating and registering an application

1. User fills in the Loan Risk Prediction form (React).
2. Frontend POSTs `input_features` to `POST /api/predictions`.
3. Backend validates with Pydantic, runs the real trained scikit-learn
   pipeline (`ml_service.py`), returns `default_probability`,
   `non_default_probability`, `risk_category`, and feature-importance-based
   risk factors.
4. User clicks "Save Application" -> `POST /api/applications`, which
   persists the application (with prediction fields) to MongoDB and logs
   an audit event.
5. User clicks "Register on Blockchain" -> `POST /api/blockchain/register/{id}`:
   - Backend loads the application from MongoDB.
   - Builds a canonical JSON representation of the immutable fields
     (`hashing_service.py`).
   - Computes a SHA-256 hash.
   - Sends a real transaction to `LoanRecordRegistry.registerRecord()` via
     web3.py, signed with a local Hardhat development key.
   - Waits for the transaction receipt, extracts the transaction hash,
     block number, and timestamp.
   - Saves this blockchain info back onto the MongoDB application document
     and into the `blockchain_records` collection.
   - Logs a "Blockchain Registered" audit event.
6. Later, `GET /api/blockchain/verify/{id}`:
   - Recomputes the canonical hash from the CURRENT MongoDB record.
   - Reads the hash stored on-chain via `verifyRecord()`.
   - Compares the two. Returns `VERIFIED` or `VERIFICATION FAILED` with
     both hashes shown.

## Why this design keeps sensitive data off-chain

Only `applicationId`, a SHA-256 `recordHash`, `riskCategory`, a timestamp,
and the registrar's address go on-chain. Applicant income, credit score,
loan amount, etc. remain in MongoDB only. The blockchain's role is purely
tamper-evidence: proving that a MongoDB record has (or hasn't) been altered
since registration, without exposing the record's contents publicly.
