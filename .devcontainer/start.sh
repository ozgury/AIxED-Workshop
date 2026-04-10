#!/bin/bash
# Auto-starts WildCard every time the Codespace starts/restarts
# Serves everything from port 8000 (no separate frontend server needed)

echo "=== Waiting for PostgreSQL ==="
for i in {1..30}; do
  pg_isready -h localhost -U wildcard 2>/dev/null && break
  sleep 1
done

echo "=== Building frontend ==="
cd /workspace/frontend
npm run build 2>&1 | tail -3

echo "=== Making port 8000 public ==="
gh codespace ports visibility 8000:public -c $CODESPACE_NAME 2>/dev/null || true

echo "=== Starting backend (serves everything) ==="
# Kill any existing backend
kill $(lsof -ti:8000) 2>/dev/null || true
sleep 1
cd /workspace/backend
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
echo "Backend PID: $!"

sleep 3
echo ""
echo "========================================="
echo "  WildCard is running!"
echo ""
echo "  Open: https://${CODESPACE_NAME}-8000.app.github.dev/"
echo ""
echo "  Log:  tail -f /tmp/backend.log"
echo ""
if [ -z "$ANTHROPIC_API_KEY" ]; then
echo "  WARNING: ANTHROPIC_API_KEY is not set."
echo "  'Ask Questions' mode won't work without it."
fi
echo "========================================="
