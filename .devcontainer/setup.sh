#!/bin/bash
set -e

echo "=== Installing Node.js 22 ==="
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt-get install -y nodejs

echo "=== Installing backend dependencies ==="
cd /workspace/backend
pip install --quiet fastapi "uvicorn[standard]" "sqlalchemy[asyncio]" asyncpg psycopg2-binary \
  alembic pgvector pydantic pydantic-settings python-multipart pandas openpyxl \
  PyMuPDF python-docx sentence-transformers anthropic python-dotenv aiofiles

echo "=== Installing frontend dependencies ==="
cd /workspace/frontend
npm install

echo "=== Waiting for PostgreSQL ==="
for i in {1..30}; do
  pg_isready -h localhost -U wildcard && break
  sleep 1
done

echo "=== Enabling pgvector extension ==="
PGPASSWORD=wildcard psql -h localhost -U wildcard -d wildcard -c "CREATE EXTENSION IF NOT EXISTS vector;" || true

echo ""
echo "========================================="
echo "  WildCard is ready!"
echo ""
echo "  1. Set your Anthropic API key:"
echo "     export ANTHROPIC_API_KEY=sk-ant-..."
echo ""
echo "  2. Start backend:"
echo "     cd /workspace/backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "  3. Start frontend (new terminal):"
echo "     cd /workspace/frontend && npm run dev -- --host 0.0.0.0"
echo ""
echo "========================================="
