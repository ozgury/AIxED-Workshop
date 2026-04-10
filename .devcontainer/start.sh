#!/bin/bash
# Start WildCard - installs deps if needed, then starts the server

cd /workspace

# Install Python deps if missing
if ! python3 -c "import uvicorn" 2>/dev/null; then
  echo "=== Installing Python dependencies ==="
  pip install --quiet fastapi "uvicorn[standard]" "sqlalchemy[asyncio]" asyncpg psycopg2-binary \
    alembic pgvector pydantic pydantic-settings python-multipart pandas openpyxl \
    PyMuPDF python-docx sentence-transformers anthropic python-dotenv aiofiles
fi

# Wait for PostgreSQL
echo "=== Waiting for PostgreSQL ==="
for i in {1..30}; do
  pg_isready -h localhost -U wildcard 2>/dev/null && break
  sleep 1
done
PGPASSWORD=wildcard psql -h localhost -U wildcard -d wildcard -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>/dev/null || true

# Make port public
gh codespace ports visibility 8000:public -c $CODESPACE_NAME 2>/dev/null || true

# Kill old server if any
kill $(lsof -ti:8000) 2>/dev/null || true
sleep 1

# Start backend
echo "=== Starting WildCard ==="
cd /workspace/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &

sleep 3
if curl -s localhost:8000/api/health > /dev/null; then
  echo ""
  echo "========================================="
  echo "  WildCard is running!"
  echo "  https://${CODESPACE_NAME}-8000.app.github.dev/"
  echo "========================================="
else
  echo "ERROR: Server failed to start. Log:"
  cat /tmp/backend.log
fi
