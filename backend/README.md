# LoanDefault MLBC - Backend

FastAPI backend connecting the trained ML model, MongoDB, and the
LoanRecordRegistry smart contract (via web3.py).

## Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

`BLOCKCHAIN_CONTRACT_ADDRESS` can be left blank -- the backend will
automatically read `blockchain/deployed-address.json` if present.

## Prerequisites

1. **MongoDB** running (see root `docker-compose.yml`) at the URI in `.env`.
2. **ML model trained**: from `ml/`, run `python scripts/generate_demo_data.py`
   then `python scripts/train_model.py`.
3. **Blockchain** (optional): a local Hardhat node with the contract
   deployed (see `blockchain/README.md`).

## Run

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API docs: http://127.0.0.1:8000/docs

## Seed demo data

```bash
python scripts/seed_mongodb.py --register-on-chain
```

## Tests

```bash
pytest
```

- ML-dependent tests skip automatically if the model hasn't been trained yet.
- `tests/test_blockchain.py` skips automatically unless a local Hardhat
  node + deployed contract are reachable at `BLOCKCHAIN_RPC_URL` -- when
  they are, these tests perform REAL on-chain transactions.
- Everything else runs against `mongomock` (in-memory MongoDB-compatible
  engine), exercising the full API/service/repository stack.

## Architecture

```
app/
  main.py         FastAPI app, CORS, router wiring
  config.py       Settings from environment
  database.py     MongoDB connection + indexes
  dependencies.py FastAPI DI helpers
  api/            One router per resource
  schemas/        Pydantic request/response models
  services/       Business logic
  repositories/   Direct MongoDB access
```

See the root README for the full API list.
