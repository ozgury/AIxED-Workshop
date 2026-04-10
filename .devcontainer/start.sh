#!/bin/bash
# Start WildCard - frontend is pre-built, just start the backend

echo "=== Waiting for PostgreSQL ==="
for i in {1..30}; do
  pg_isready -h localhost -U wildcard 2>/dev/null && break
  sleep 1
done

echo "=== Making port public ==="
gh codespace ports visibility 8000:public -c $CODESPACE_NAME 2>/dev/null || true

echo "=== Starting WildCard ==="
kill $(lsof -ti:8000) 2>/dev/null || true
sleep 1
cd /workspace/backend
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &

sleep 2
echo ""
curl -s localhost:8000/api/health && echo " - Backend OK"
echo ""
echo "========================================="
echo "  WildCard is running!"
echo "  https://${CODESPACE_NAME}-8000.app.github.dev/"
echo "========================================="
