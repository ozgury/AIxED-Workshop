#!/bin/bash
# Quick fix: make ports public and verify servers
gh codespace ports visibility 5173:public 8000:public -c $CODESPACE_NAME 2>/dev/null || true

# Check if servers are running, restart if needed
if ! curl -s localhost:8000/api/health > /dev/null 2>&1; then
  echo "Starting backend..."
  cd /workspace/backend
  nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
fi

if ! curl -s localhost:5173 > /dev/null 2>&1; then
  echo "Starting frontend..."
  cd /workspace/frontend
  nohup npm run dev -- --host 0.0.0.0 > /tmp/frontend.log 2>&1 &
fi

sleep 2
echo ""
echo "Backend:"
curl -s localhost:8000/api/health || echo "NOT RUNNING"
echo ""
echo "Frontend:"
curl -s -o /dev/null -w "HTTP %{http_code}" localhost:5173 || echo "NOT RUNNING"
echo ""
echo ""
echo "Ports are now public. Open this URL:"
echo "https://${CODESPACE_NAME}-5173.app.github.dev/"
