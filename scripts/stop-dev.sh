#!/usr/bin/env bash
# Stops services started by start-dev.sh.
for name in hardhat backend frontend; do
  pidfile="/tmp/loan-mlbc-${name}.pid"
  if [ -f "$pidfile" ]; then
    pid=$(cat "$pidfile")
    kill "$pid" 2>/dev/null && echo "Stopped $name (pid $pid)" || echo "$name was not running"
    rm -f "$pidfile"
  fi
done

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
docker compose -f "$ROOT_DIR/docker-compose.yml" down
echo "Stopped MongoDB."
