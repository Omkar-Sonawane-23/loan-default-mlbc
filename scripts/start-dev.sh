#!/usr/bin/env bash
# Starts MongoDB (via Docker), a local Hardhat node, the backend, and the
# frontend, each in the background, with logs written to /tmp.
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Starting MongoDB..."
docker compose -f "$ROOT_DIR/docker-compose.yml" up -d mongodb

echo "Starting local Hardhat blockchain node..."
cd "$ROOT_DIR/blockchain"
nohup npx hardhat node > /tmp/loan-mlbc-hardhat.log 2>&1 &
echo $! > /tmp/loan-mlbc-hardhat.pid
sleep 5

echo "Deploying smart contract..."
npm run deploy:local

echo "Starting backend..."
cd "$ROOT_DIR/backend"
source .venv/bin/activate
nohup uvicorn app.main:app --host 127.0.0.1 --port 8000 > /tmp/loan-mlbc-backend.log 2>&1 &
echo $! > /tmp/loan-mlbc-backend.pid
deactivate

echo "Starting frontend..."
cd "$ROOT_DIR/frontend"
nohup npm run dev > /tmp/loan-mlbc-frontend.log 2>&1 &
echo $! > /tmp/loan-mlbc-frontend.pid

echo ""
echo "All services starting. Logs in /tmp/loan-mlbc-*.log"
echo "  Frontend:  http://localhost:5173"
echo "  Backend:   http://127.0.0.1:8000/docs"
echo "  Hardhat:   http://127.0.0.1:8545"
echo "Run scripts/stop-dev.sh to stop everything."
