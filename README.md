# LoanDefault MLBC

**Machine Learning-Based Loan Default Risk Prediction and Blockchain-Based
Loan Record Management System**

An academic mini-project combining Machine Learning, FastAPI, React,
MongoDB, Solidity, and Hardhat to predict loan default risk and provide
tamper-evident, blockchain-backed audit trails for loan risk records.

> **Academic disclaimer**: This system is an academic Machine Learning and
> Blockchain demonstration. The predicted default probability is an
> estimated model output and is not financial advice, a guaranteed
> prediction, or an automated loan approval/rejection decision. The
> dataset is entirely synthetic.

---

## Table of Contents

1. [Problem Statement & Objectives](#problem-statement--objectives)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Technology Stack](#technology-stack)
5. [Machine Learning](#machine-learning)
6. [Blockchain](#blockchain)
7. [Database](#database)
8. [Backend API](#backend-api)
9. [Frontend](#frontend)
10. [Folder Structure](#folder-structure)
11. [Environment Variables](#environment-variables)
12. [Installation & Setup](#installation--setup)
13. [Complete Run Instructions](#complete-run-instructions)
14. [Testing](#testing)
15. [Troubleshooting](#troubleshooting)
16. [Limitations & Future Scope](#limitations--future-scope)
17. [Presentation Flow & Viva Questions](#presentation-flow--viva-questions)
18. [Conclusion](#conclusion)

---

## Problem Statement & Objectives

Financial institutions need to assess loan default risk quickly and
consistently, while also being able to prove that a stored risk
assessment hasn't been tampered with after the fact. This project builds:

1. A **real, trained ML model** that predicts loan default probability
   from applicant and loan features.
2. A **FastAPI + MongoDB backend** that manages the full lifecycle of a
   loan application: prediction, storage, review, status tracking, and
   audit logging.
3. A **Solidity smart contract on a local Ethereum blockchain** that
   stores a tamper-evident hash of each risk assessment, so any later
   modification to the stored record can be detected.
4. A **React frontend** presenting all of the above as a professional,
   internal fintech-style application.

## Product scope and implementation status

This repository remains an academic research/demo application, not a production credit-decision service. The current build includes local SHAP explanations, sigmoid-calibrated default probabilities trained/evaluated on synthetic data, a derived demo risk index, an ETH-denominated Solidity loan lifecycle, injected-wallet transaction UX, MongoDB transaction indexing and reconciliation, and on-chain contract-derived repayment reputation. The end-to-end local-EVM plus FastAPI/Mongo-mock scenario is tested. It is not validated for real borrowers, stablecoin/fiat lending, or production use. There is still no authentication/RBAC, and a hash/calibration does not prove prediction correctness. Human review is required.

The repository analysis and upgrade notes are in [docs/UPGRADE_PLAN.md](docs/UPGRADE_PLAN.md). Credit-risk metrics/calibration use a held-out synthetic test split only; the derived 0–1000 score is a research index, not a bureau score or externally validated measure. The loan lifecycle transfers native test-chain currency (ETH on Hardhat), not rupees or stablecoins. Wallet actions require an injected wallet on the configured chain. Reconciliation indexes confirmed contract events into MongoDB and compares snapshots with current state; it is demo-grade and not authenticated. PSI monitoring remains a screening signal, not outcome performance or fairness monitoring. SHAP scope and the on-chain loan contract are documented in [docs/explainability.md](docs/explainability.md) and [docs/loan-lifecycle.md](docs/loan-lifecycle.md).

## Features

- Real-time calibrated-on-synthetic ML probability with local SHAP log-odds contributions and global feature importance clearly separated
- Human-readable demo risk index and assumption-labeled expected loss
- MetaMask/injected EVM wallet connection, chain/balance display, and real transaction confirmation UX
- Solidity loan states, agreement acknowledgement, ETH funding, partial/full repayments, defaults, and contract-derived reputation
- Confirmed transaction indexing and database ↔ chain reconciliation dashboard
- Full application lifecycle management (create, view, edit, status,
  delete) with search, filtering, sorting, and pagination
- Complete audit trail per application
- Blockchain registration and tamper-evidence verification
- Dashboard and analytics with live-computed statistics and charts
- CSV/JSON export of all applications; per-application PDF report
- Settings page showing live system/service status (no secrets exposed)

## Architecture

```
React Frontend (Vite/TS/Tailwind)
      |  REST API (axios)
      v
FastAPI Backend
      |                    |
      v                    v
ML Service (scikit-learn)   MongoDB
      |
      v
Risk Prediction
      |
FastAPI --- web3.py ---> Hardhat / configured EVM
      |                         |
      v                         +-- LoanRecordRegistry.sol (hash proof)
MongoDB                     +-- LoanLifecycle.sol (loan state, ETH, reputation)
      ^                         |
      +---- verified event snapshots/reconciliation
```

See `docs/architecture.md` for the detailed request flow.

## Technology Stack

**Frontend**: React 18, Vite, TypeScript, Tailwind CSS, React Router,
Axios, Recharts, Lucide React

**Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic, Pandas, NumPy,
Scikit-learn, Joblib, PyMongo, web3.py, python-dotenv, ReportLab

**Database**: MongoDB 7

**Blockchain**: Solidity 0.8.24, Hardhat, TypeScript, Ethers.js, local
Hardhat Ethereum network (chain id 31337)

## Machine Learning

Full details: `docs/ml-documentation.md` and `ml/README.md`.

- **6,000-row synthetic dataset**, reproducible with a fixed random seed,
  ~21.5% default rate.
- **4 models trained and compared**: Logistic Regression, Decision Tree,
  Random Forest, Gradient Boosting -- all through a single scikit-learn
  `Pipeline` (`ColumnTransformer` + classifier), so training and
  inference use identical preprocessing.
- **Best model auto-selected by ROC-AUC** on a held-out, stratified 20%
  test split. In the reference run: **Logistic Regression**, ROC-AUC
  **0.8626**, accuracy **86.58%** (see `ml/README.md` for the full
  4-model comparison table with exact numbers from an actual run).
- **Feature importance** computed from the real fitted model (logistic
  regression coefficients, or impurity-based importance for tree
  models) -- surfaced in every prediction response and on the Model
  Analytics page.
- Demonstration-only risk thresholds: LOW < 30%, MEDIUM 30-70%, HIGH >= 70%.

## Blockchain

Full details: `docs/blockchain-documentation.md` and `blockchain/README.md`.

- `LoanRecordRegistry.sol` stores only `applicationId`, a SHA-256
  `recordHash`, `riskCategory`, `timestamp`, and `registrar` -- never
  applicant income, credit score, loan amount, or any other sensitive
  field.
- Functions: `registerRecord`, `getRecord`, `recordExists`,
  `verifyRecord`, `getRecordTimestamp`. Duplicate registration reverts.
- **8/8 Hardhat tests passing** (see `blockchain/test/LoanRecordRegistry.ts`).
- Verified end-to-end during development: deployed to a live local
  Hardhat node, registered a real record, read it back, and confirmed
  `VERIFIED` -- see `tests/end-to-end/README.md` for the full log of
  what was actually run.
- Backend communicates via **web3.py** (not a JS bridge), sending real
  signed transactions and waiting for receipts.

## Database

MongoDB database `loan_default_mlbc` with collections `applications`,
`audit_logs`, `blockchain_records`, `model_metadata`. Full schema with
example documents: `docs/database-schema.md`.

## Backend API

All endpoints listed in `docs/api-documentation.md`. Summary:

```
GET  /api/health
GET  /api/model/info
GET  /api/model/metrics
POST /api/predictions
POST /api/applications
GET  /api/applications
GET  /api/applications/{id}
PUT  /api/applications/{id}
DELETE /api/applications/{id}
PATCH /api/applications/{id}/status
GET  /api/applications/{id}/audit
GET  /api/dashboard/stats
GET  /api/analytics
POST /api/blockchain/register/{id}
GET  /api/blockchain/record/{id}
GET  /api/blockchain/verify/{id}
GET  /api/blockchain/status
GET  /api/blockchain/transactions
GET  /api/export/applications
GET  /api/export/applications/{id}/pdf
```

Interactive docs at `http://127.0.0.1:8000/docs` when the backend is running.

## Frontend

Pages: Dashboard, Risk Prediction, Applications, Application Details,
Analytics, Model Analytics, Blockchain, Verify Record, Settings. Every
page calls the real backend API -- see `frontend/README.md`.

## Folder Structure

```
loan-default-mlbc/
├── README.md, LICENSE, .gitignore, .env.example, docker-compose.yml
├── docs/                    architecture, API, ML, blockchain, schema, workflow, viva docs
├── backend/                 FastAPI app, tests, requirements.txt
├── frontend/                React/Vite/TS app
├── ml/                      dataset generation, training, evaluation, seeding
├── blockchain/               Solidity contract, Hardhat config, tests
├── scripts/                 setup.sh, start-dev.sh, stop-dev.sh, health-check.sh
└── tests/end-to-end/        record of the real end-to-end verification run
```

(Each of `backend/`, `frontend/`, `ml/`, `blockchain/` also has its own
detailed `README.md`.)

## Environment Variables

Root `.env.example` lists all variables; `backend/.env.example` and
`frontend/.env.example` are the actual per-service files used:

```
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=loan_default_mlbc
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
BLOCKCHAIN_RPC_URL=http://127.0.0.1:8545
BLOCKCHAIN_PRIVATE_KEY=
BLOCKCHAIN_CONTRACT_ADDRESS=
BLOCKCHAIN_CHAIN_ID=31337
MODEL_PATH=../ml/models/loan_default_model.joblib
MODEL_VERSION=rf-v1
CORS_ORIGINS=http://localhost:5173
VITE_API_URL=http://127.0.0.1:8000/api
```

No real private keys or secrets are ever required or committed --
`BLOCKCHAIN_PRIVATE_KEY` can be left blank to use Hardhat's well-known
local development key automatically (see `blockchain_service.py`).

## Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (for MongoDB via `docker-compose.yml`), or a local MongoDB install

### Quick setup
```bash
./scripts/setup.sh
```

### Manual setup (step by step)

**1. MongoDB**
```bash
docker compose up -d mongodb
```

**2. ML**
```bash
cd ml
pip install -r ../backend/requirements.txt
python scripts/generate_demo_data.py
python scripts/train_model.py
python scripts/seed_demo_applications.py
```

**3. Blockchain**
```bash
cd blockchain
npm install
npm run compile
npx hardhat node            # keep running in its own terminal
npm run deploy:local        # hash registry
npm run deploy:lifecycle:local # separate loan lifecycle contract; outputs local address
```

**4. Backend**
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

**5. Seed demo data (optional)**
```bash
cd backend
python scripts/seed_mongodb.py --register-on-chain
```

**6. Frontend**
```bash
cd frontend
npm install
cp .env.example .env
# Set VITE_LOAN_LIFECYCLE_ADDRESS from blockchain/loan-lifecycle-address.json
npm run dev
```

For the `/loans` demo connect an injected wallet configured for chain `31337` and a compatible RPC endpoint. Contract actions use native test currency only. Keep the local Hardhat node running; its pre-funded test keys are public and never safe for real funds.

## Complete Run Instructions

Open 4 terminals:

```bash
# Terminal 1
docker compose up mongodb

# Terminal 2
cd blockchain && npx hardhat node

# Terminal 3 (after terminal 2 is running)
cd blockchain && npm run deploy:local && npm run deploy:lifecycle:local
cd ../backend && source .venv/bin/activate && uvicorn app.main:app --reload

# Terminal 4
cd frontend && npm run dev
```

Then open `http://localhost:5173`.

## Testing

```bash
# Smart contract tests (15 tests)
cd blockchain && npm test

# Backend tests (includes real local EVM transaction/reconciliation test;
# lifecycle and registry deployments must be available for chain tests)
cd backend && pytest

# Frontend type-check + build
cd frontend && npm run build
```

See `tests/end-to-end/README.md` for the full record of what was actually
run and verified during development, including exact pass counts and
model metrics.

## Troubleshooting

- **`ML model not found`**: run `python ml/scripts/train_model.py` first
  (requires `generate_demo_data.py` to have been run).
- **Blockchain endpoints return 503**: no local Hardhat node is running,
  or the contract isn't deployed. Start `npx hardhat node` and run
  `npm run deploy:local` in `blockchain/`.
- **Blockchain state resets**: `npx hardhat node` is an in-memory chain --
  restarting it clears all registered records. This is expected for a
  local dev network. Re-deploy and re-register after a restart.
- **CORS errors in the browser**: confirm `CORS_ORIGINS` in
  `backend/.env` includes `http://localhost:5173`.
- **MongoDB connection errors**: confirm `docker compose up -d mongodb`
  succeeded and `MONGODB_URI` matches.

## Limitations & Future Scope

**Limitations**: synthetic, unvalidated dataset; no authentication/
authorization; local-only blockchain (not a public/consortium network);
no model monitoring or drift detection; thresholds are illustrative, not
regulatory-compliant.

**Future scope**: real (anonymized, licensed) credit data with fairness
auditing; user authentication and role-based access; deployment to a
public testnet with proper key management (KMS); model monitoring/
retraining pipeline; SHAP-based per-instance explanations; multi-currency
support.

## Presentation Flow & Viva Questions

See `docs/project-workflow.md` for a step-by-step demo script, and
`docs/viva-questions.md` for anticipated questions and answers covering
the ML, blockchain, and system design decisions made in this project.

## Conclusion

This project demonstrates a complete, working integration of supervised
machine learning, a REST API backend, a document database, and a
blockchain-backed tamper-evidence layer -- built and verified end-to-end
during development (real training runs, real on-chain transactions, real
passing test suites) rather than assembled from disconnected pieces.
