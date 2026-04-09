#!/bin/bash
# Auto-starts both servers every time the Codespace starts/restarts

echo "=== Waiting for PostgreSQL ==="
for i in {1..30}; do
  pg_isready -h localhost -U wildcard 2>/dev/null && break
  sleep 1
done

echo "=== Starting backend ==="
cd /workspace/backend
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
echo "Backend PID: $!"

echo "=== Starting frontend ==="
cd /workspace/frontend
nohup npm run dev -- --host 0.0.0.0 > /tmp/frontend.log 2>&1 &
echo "Frontend PID: $!"

sleep 3
echo ""
echo "========================================="
echo "  WildCard is running!"
echo ""
echo "  Frontend: port 5173 (should open automatically)"
echo "  Backend:  port 8000"
echo ""
echo "  Logs:"
echo "    tail -f /tmp/backend.log"
echo "    tail -f /tmp/frontend.log"
echo ""
if [ -z "$ANTHROPIC_API_KEY" ]; then
echo "  WARNING: ANTHROPIC_API_KEY is not set."
echo "  'Ask Questions' mode won't work without it."
echo "  Set it in Codespace secrets or run:"
echo "    export ANTHROPIC_API_KEY=sk-ant-..."
echo "  then restart the backend:"
echo "    kill \$(lsof -ti:8000); cd /workspace/backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &"
fi
echo "========================================="
