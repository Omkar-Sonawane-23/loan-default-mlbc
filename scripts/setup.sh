#!/usr/bin/env bash
# One-time setup: installs all dependencies and trains the ML model.
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Setting up ML environment and training model..."
cd "$ROOT_DIR/ml"
python3 -m venv .venv 2>/dev/null || true
source .venv/bin/activate 2>/dev/null || true
pip install -r "$ROOT_DIR/backend/requirements.txt"
python scripts/generate_demo_data.py
python scripts/train_model.py
python scripts/seed_demo_applications.py
deactivate 2>/dev/null || true

echo "==> Setting up backend..."
cd "$ROOT_DIR/backend"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp -n .env.example .env || true
deactivate

echo "==> Setting up blockchain (Hardhat)..."
cd "$ROOT_DIR/blockchain"
npm install
npm run compile

echo "==> Setting up frontend..."
cd "$ROOT_DIR/frontend"
npm install
cp -n .env.example .env || true

echo ""
echo "Setup complete. Next steps:"
echo "  1. Start MongoDB:      docker compose up -d mongodb"
echo "  2. Start a local chain: cd blockchain && npx hardhat node"
echo "  3. Deploy the contract: cd blockchain && npm run deploy:local"
echo "  4. Start the backend:   cd backend && source .venv/bin/activate && uvicorn app.main:app --reload"
echo "  5. Start the frontend:  cd frontend && npm run dev"
echo "  6. (Optional) Seed data: cd backend && python scripts/seed_mongodb.py --register-on-chain"
