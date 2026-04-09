# WildCard

A local web application that lets you upload files and ask questions about them in plain English. Upload spreadsheets and documents, then get visual answers — tables, charts, and summaries.

## Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 16 with pgvector extension
- Anthropic API key (for Claude)

## Setup

### 1. Database

Start PostgreSQL and create the database:

```bash
# Start PostgreSQL
pg_ctlcluster 16 main start

# Create user and database
sudo -u postgres psql -c "CREATE USER wildcard WITH PASSWORD 'wildcard';"
sudo -u postgres psql -c "CREATE DATABASE wildcard OWNER wildcard;"
sudo -u postgres psql -d wildcard -c "CREATE EXTENSION IF NOT EXISTS vector;"
sudo -u postgres psql -d wildcard -c "GRANT ALL ON SCHEMA public TO wildcard;"
```

### 2. Environment

Copy and edit the environment file:

```bash
cp .env.example .env
# Edit .env and set your ANTHROPIC_API_KEY
```

### 3. Backend

```bash
cd backend
pip install -e .
cd ..
```

### 4. Frontend

```bash
cd frontend
npm install
cd ..
```

## Running

Start both servers:

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

Open http://localhost:5173 in your browser.

## Usage

### Manage Data (Edit Mode)
- Drag and drop spreadsheets (CSV, Excel) or documents (PDF, Word, TXT)
- Spreadsheets are parsed and stored in the database as real tables
- Shared columns across spreadsheets are auto-detected as relationships
- Delete files to remove all associated data

### Ask Questions (Analyze Mode)
- Type any question in plain English
- The app determines whether to query spreadsheets, documents, or both
- Results appear as tables, charts, or written summaries
