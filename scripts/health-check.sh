#!/usr/bin/env bash
# Quick smoke check of all running services.
echo "Backend health:"
curl -s http://127.0.0.1:8000/api/health | python3 -m json.tool || echo "  backend not reachable"

echo ""
echo "Blockchain status:"
curl -s http://127.0.0.1:8000/api/blockchain/status | python3 -m json.tool || echo "  blockchain status not reachable"

echo ""
echo "Frontend:"
curl -s -o /dev/null -w "  HTTP %{http_code}\n" http://localhost:5173 || echo "  frontend not reachable"
