# WildCard — Implementation Plan

## 1. Overview

WildCard is a local web application that lets users upload files (spreadsheets and documents), stores them in a structured database, and answers natural language questions about the data with clean visual results — tables, charts, or written summaries.

The app has two modes:

- **Edit Mode** — Upload and manage spreadsheets (Excel/CSV) and documents (PDF, Word, TXT). Spreadsheets are stored as real database tables. Shared column names across spreadsheets are auto-detected as relationships.
- **Analyze Mode** — Ask questions in plain English. The app determines whether to query spreadsheets, documents, or both, and returns a visual answer.

The system is fully schema-agnostic — it works with any uploaded data regardless of topic, industry, or column names.

---

## 2. Tech Stack

### Backend

| Component | Choice | Rationale |
|---|---|---|
| Web framework | **FastAPI** | Async-native, automatic OpenAPI docs, Pydantic validation |
| Database ORM | **SQLAlchemy 2.0** (async) | Dynamic table creation/introspection; mature PostgreSQL support |
| Migrations | **Alembic** | For metadata tables only; dynamic user tables are managed programmatically |
| Spreadsheet parsing | **pandas** + **openpyxl** | Robust Excel/CSV parsing with dtype inference |
| PDF parsing | **PyMuPDF (fitz)** | Fast, accurate text extraction with layout preservation |
| Word parsing | **python-docx** | Standard .docx parsing |
| Vector embeddings | **pgvector** extension for PostgreSQL | Single database for everything; no separate vector store |
| Embedding model | **sentence-transformers** (`all-MiniLM-L6-v2`) | Runs locally, fast, 384-dim vectors |
| LLM | **Anthropic Claude API** (`claude-sonnet-4-20250514`) | SQL generation, question routing, document Q&A, result synthesis |

### Frontend

| Component | Choice | Rationale |
|---|---|---|
| Framework | **React 18** with **TypeScript** | Strong typing for complex state |
| Build tool | **Vite** | Fast HMR, simple config |
| UI library | **Shadcn/ui** (Radix + Tailwind) | Accessible, clean, non-technical look |
| State management | **TanStack Query (React Query)** | Server-state caching, automatic refetch |
| Charts | **Recharts** | React-native, declarative, handles bar/line/pie |
| Markdown rendering | **react-markdown** | For LLM narrative summaries |
| HTTP client | **axios** | Clean API for file uploads with interceptors |

### Infrastructure

| Component | Choice | Rationale |
|---|---|---|
| Database | **PostgreSQL 16** + **pgvector** | Single DB for structured data, metadata, and vector search |
| Containerization | **Docker Compose** | One command to start PostgreSQL locally |
| Python | **3.11+** | Modern async features |
| Node | **20 LTS** | Current stable |

---

## 3. Project Structure

```
wildcard/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── PLAN.md
│
├── backend/
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app factory, CORS, lifespan
│   │   ├── config.py                  # Settings via pydantic-settings
│   │   ├── database.py                # Async engine, session factory
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── metadata.py            # ORM: UploadedFile, ColumnRelationship, DocumentChunk
│   │   │   └── dynamic.py             # Utilities for creating/dropping dynamic tables
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── files.py               # Pydantic: FileUploadResponse, FileListResponse
│   │   │   ├── query.py               # Pydantic: QueryRequest, QueryResponse, ChartData
│   │   │   └── relationships.py       # Pydantic: RelationshipInfo
│   │   │
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── files.py               # POST /files/upload, GET /files, DELETE /files/{id}
│   │   │   ├── query.py               # POST /query
│   │   │   └── schema.py              # GET /schema (introspection for LLM context)
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── file_processor.py      # Dispatch to spreadsheet or document processor
│   │   │   ├── spreadsheet_processor.py  # Parse, infer types, create table, insert
│   │   │   ├── document_processor.py  # Extract text, chunk, embed, store
│   │   │   ├── relationship_detector.py  # Detect shared columns across tables
│   │   │   ├── query_router.py        # Classify question, orchestrate LLM calls
│   │   │   ├── sql_generator.py       # Build schema context, call Claude for SQL
│   │   │   ├── document_searcher.py   # Vector similarity search
│   │   │   └── response_formatter.py  # Decide table vs chart vs summary
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── type_inference.py      # Map pandas dtypes to PostgreSQL types
│   │       ├── sanitization.py        # Sanitize table/column names for SQL safety
│   │       └── chunking.py            # Text chunking strategies for documents
│   │
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_spreadsheet_processor.py
│   │   ├── test_document_processor.py
│   │   ├── test_relationship_detector.py
│   │   ├── test_query_router.py
│   │   └── test_sql_generator.py
│   │
│   └── uploads/                        # Raw uploaded files (gitignored)
│
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── index.html
│   │
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── index.css                   # Tailwind base styles
│       │
│       ├── api/
│       │   ├── client.ts              # Axios instance with base URL
│       │   ├── files.ts               # uploadFile, listFiles, deleteFile
│       │   └── query.ts               # submitQuery
│       │
│       ├── components/
│       │   ├── layout/
│       │   │   ├── AppShell.tsx        # Top-level layout: header + content area
│       │   │   ├── Header.tsx          # App title + mode toggle
│       │   │   └── ModeToggle.tsx      # Edit/Analyze segmented control
│       │   │
│       │   ├── edit/
│       │   │   ├── EditMode.tsx        # Container for Edit Mode
│       │   │   ├── FileUploader.tsx    # Drag-and-drop upload zone
│       │   │   ├── SpreadsheetList.tsx # Table of uploaded spreadsheets
│       │   │   ├── DocumentList.tsx    # Table of uploaded documents
│       │   │   ├── RelationshipMap.tsx # Visual display of shared column relationships
│       │   │   └── FileCard.tsx        # Individual file row with delete button
│       │   │
│       │   ├── analyze/
│       │   │   ├── AnalyzeMode.tsx     # Container for Analyze Mode
│       │   │   ├── QueryInput.tsx      # Text input for natural language questions
│       │   │   ├── ResultDisplay.tsx   # Router: renders table, chart, or summary
│       │   │   ├── DataTable.tsx       # Tabular result display
│       │   │   ├── ChartDisplay.tsx    # Recharts wrapper for chart types
│       │   │   ├── SummaryDisplay.tsx  # Markdown-rendered narrative answer
│       │   │   └── QueryHistory.tsx    # Recent questions sidebar
│       │   │
│       │   └── shared/
│       │       ├── LoadingSpinner.tsx
│       │       ├── ErrorBanner.tsx
│       │       └── ConfirmDialog.tsx   # Delete confirmation
│       │
│       ├── hooks/
│       │   ├── useFiles.ts            # React Query hooks for file operations
│       │   ├── useAnalyze.ts          # React Query hook for Q&A
│       │   └── useMode.ts             # Mode state (edit/analyze) with localStorage
│       │
│       ├── types/
│       │   ├── files.ts               # TypeScript interfaces matching backend schemas
│       │   ├── query.ts
│       │   └── relationships.ts
│       │
│       └── lib/
│           └── utils.ts               # Tailwind merge utility, formatters
│
└── test-data/                          # Sample files for validation (gitignored)
```

---

## 4. Database Design

### 4.1 Metadata Tables (managed via Alembic)

**`uploaded_files`** — tracks every uploaded file:

```sql
CREATE TABLE uploaded_files (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_name   TEXT NOT NULL,
    stored_path     TEXT NOT NULL,
    file_type       TEXT NOT NULL,          -- 'spreadsheet' | 'document'
    mime_type       TEXT NOT NULL,
    file_size       BIGINT NOT NULL,
    table_name      TEXT,                   -- only for spreadsheets: dynamic table name
    row_count       INTEGER,               -- only for spreadsheets
    column_names    JSONB,                 -- only for spreadsheets: ["col1", "col2", ...]
    status          TEXT NOT NULL DEFAULT 'processing',
    error_message   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**`column_relationships`** — auto-detected shared columns:

```sql
CREATE TABLE column_relationships (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    column_name     TEXT NOT NULL UNIQUE,
    table_names     JSONB NOT NULL,         -- ["wc_abc_programs", "wc_def_enrollments"]
    file_ids        JSONB NOT NULL,         -- [uuid1, uuid2]
    detected_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**`document_chunks`** — chunked and embedded document text:

```sql
CREATE TABLE document_chunks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id         UUID NOT NULL REFERENCES uploaded_files(id) ON DELETE CASCADE,
    chunk_index     INTEGER NOT NULL,
    content         TEXT NOT NULL,
    embedding       vector(384) NOT NULL,
    metadata        JSONB,                  -- page number, section heading, etc.
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_chunks_file ON document_chunks(file_id);
CREATE INDEX idx_chunks_embedding ON document_chunks
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

### 4.2 Dynamic Tables (one per spreadsheet)

Each uploaded spreadsheet becomes its own PostgreSQL table:

- **Naming**: `wc_{file_id_short}_{sanitized_filename}` (e.g., `wc_a1b2c3_student_enrollments`)
- **Column names**: Sanitized — lowercase, underscores for spaces, special chars stripped
- **Type mapping** from pandas dtypes:
  - `int64` → `BIGINT`
  - `float64` → `DOUBLE PRECISION`
  - `object` (string) → `TEXT`
  - `datetime64` → `TIMESTAMPTZ`
  - `bool` → `BOOLEAN`
  - Fallback → `TEXT`
- Each table gets an internal `_wc_row_id SERIAL PRIMARY KEY` (excluded from LLM context)

---

## 5. API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/files/upload` | Upload one or more files (multipart/form-data) |
| `GET` | `/api/files` | List all uploaded files with metadata |
| `GET` | `/api/files/{id}` | Get single file details |
| `DELETE` | `/api/files/{id}` | Delete file + dynamic table + document chunks |
| `GET` | `/api/relationships` | List detected column relationships |
| `GET` | `/api/schema` | Full schema context (tables, columns, types, relationships) |
| `POST` | `/api/query` | Submit natural language question, get structured response |

---

## 6. File Processing Pipeline

### Spreadsheet Processing

```
Upload received
  → Save raw file to uploads/
  → Record in uploaded_files (status='processing')
  → pandas.read_excel() or pandas.read_csv()
  → Sanitize column names
  → Infer PostgreSQL column types
  → CREATE TABLE via SQLAlchemy DDL
  → Bulk INSERT rows (COPY for >1000 rows)
  → Update uploaded_files: status='ready', row_count, column_names, table_name
  → Trigger relationship detection
```

### Document Processing

```
Upload received
  → Save raw file to uploads/
  → Record in uploaded_files (status='processing')
  → Extract text:
       PDF  → PyMuPDF (page-by-page)
       DOCX → python-docx (paragraph-by-paragraph)
       TXT  → direct read
  → Chunk text (500 tokens per chunk, 50 token overlap)
  → Generate embeddings (sentence-transformers)
  → INSERT chunks into document_chunks with embeddings
  → Update uploaded_files: status='ready'
```

### Relationship Detection

Triggered after each spreadsheet upload:

1. Gather `column_names` from all spreadsheet rows in `uploaded_files`
2. Build a dict: `{column_name: [table1, table2, ...]}`
3. Filter to entries appearing in 2+ tables
4. For each candidate, verify with a value overlap check (query 10 distinct values from each table, check intersection)
5. Upsert confirmed relationships into `column_relationships`

---

## 7. LLM Integration Strategy

The query pipeline uses Claude in a multi-step process:

### Step 1: Query Routing (`query_router.py`)

A first Claude call classifies the question:

**Input context**: List of spreadsheet tables (with columns and row counts), list of documents (with filenames), list of detected relationships.

**Output**:
```json
{
  "query_type": "spreadsheet | document | hybrid",
  "relevant_tables": ["wc_abc_programs"],
  "relevant_documents": ["strategic_plan.pdf"],
  "needs_join": true,
  "join_column": "program_code"
}
```

### Step 2a: SQL Generation (`sql_generator.py`) — for spreadsheet queries

A second Claude call generates SQL:

**Input context**: `CREATE TABLE` statements for relevant tables (auto-generated from introspection), relationship info, sample values (first 3 rows).

**Output**:
```json
{
  "sql": "SELECT p.program_name, e.enrollment ... JOIN ... ON program_code",
  "explanation": "This query joins programs and enrollments..."
}
```

**Safety**: SQL runs in a read-only transaction. A regex pre-check rejects DDL keywords.

### Step 2b: Document Search (`document_searcher.py`) — for document queries

1. Embed the user's question with the same sentence-transformers model
2. Vector similarity search: `SELECT content FROM document_chunks ORDER BY embedding <=> $query_embedding LIMIT 10`
3. Pass retrieved chunks + question to Claude for synthesis
4. Return narrative summary

### Step 3: Hybrid Synthesis

For questions spanning both spreadsheets and documents:
1. Run SQL execution and document search in parallel (`asyncio.gather`)
2. Pass both result sets to Claude with a synthesis prompt
3. Return combined response

### Response Formatting (`response_formatter.py`)

Heuristics determine display type:
- Single scalar value → summary
- 1-2 columns with one numeric → bar chart
- Time series (date + numeric) → line chart
- Categorical + numeric (≤8 categories) → pie chart
- Multiple columns, many rows → table
- Document-only → markdown summary
- Hybrid → summary + optional supporting table/chart

**Query response schema**:
```python
class QueryResponse(BaseModel):
    answer_text: str              # Natural language explanation (always present)
    display_type: str             # "table" | "bar_chart" | "line_chart" | "pie_chart" | "summary"
    table_data: Optional[dict]    # {"columns": [...], "rows": [...]}
    chart_data: Optional[dict]    # {"labels": [...], "datasets": [...], "chart_type": "..."}
    sql_used: Optional[str]       # The executed SQL (for transparency)
    sources: list[str]            # Which files/tables contributed
```

---

## 8. Frontend Architecture

### Component Hierarchy

```
App
└── AppShell
    ├── Header
    │   ├── Logo / Title ("WildCard")
    │   └── ModeToggle ("Manage Data" | "Ask Questions")
    │
    ├── EditMode (when mode === 'edit')
    │   ├── FileUploader (drag-and-drop zone)
    │   ├── SpreadsheetList
    │   │   └── FileCard[] (name, row count, columns, delete)
    │   ├── DocumentList
    │   │   └── FileCard[] (name, type, delete)
    │   └── RelationshipMap (shared columns visualized)
    │
    └── AnalyzeMode (when mode === 'analyze')
        ├── QueryInput (text area + submit)
        ├── ResultDisplay
        │   ├── DataTable (sortable, paginated)
        │   ├── ChartDisplay (Recharts bar/line/pie)
        │   └── SummaryDisplay (react-markdown)
        └── QueryHistory (recent questions sidebar)
```

### State Management

No global state library needed. TanStack Query handles all server state. Client-side state:
- **Mode** (`edit` | `analyze`): `useState` persisted to `localStorage` via `useMode` hook
- **Query history**: Stored in TanStack Query cache

### Key UI Decisions

- **ModeToggle**: Segmented control in the header — two clear labels, not a hamburger menu
- **FileUploader**: Large drag-and-drop zone with accepted file type hints and upload progress
- **RelationshipMap**: Simple card-and-line layout showing which tables share columns
- **QueryInput**: Large centered text area (like a search bar), submit with button or Ctrl+Enter
- **ResultDisplay**: Always shows `answer_text` as a header, with collapsible "Show SQL" for transparency

---

## 9. Security Considerations for SQL Execution

Since the LLM generates SQL executed against a real database, this is the highest-risk component:

1. **Read-only transactions**: Every generated query runs inside `SET TRANSACTION READ ONLY`
2. **Keyword blocklist**: Regex pre-check rejects `INSERT`, `UPDATE`, `DELETE`, `DROP`, `CREATE`, `ALTER`, `TRUNCATE`, `GRANT`, `COPY`, `pg_`, `EXECUTE`, `DO $$`
3. **Separate database user**: Query execution uses a PostgreSQL role with `SELECT`-only grants; table creation/deletion uses a separate admin role
4. **Statement timeout**: `SET statement_timeout = '30s'` prevents runaway queries
5. **Row limit**: Results capped at 10,000 rows

---

## 10. Configuration

**`.env.example`**:
```
# Database
DATABASE_URL=postgresql+asyncpg://wildcard:wildcard@localhost:5432/wildcard
DATABASE_URL_SYNC=postgresql://wildcard:wildcard@localhost:5432/wildcard

# Claude API
ANTHROPIC_API_KEY=sk-ant-...

# App
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=50
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Frontend
VITE_API_URL=http://localhost:8000/api
```

**`docker-compose.yml`**: Single `postgres` service using `pgvector/pgvector:pg16`, exposing port 5432.

---

## 11. Implementation Phases

### Phase 1: Foundation

**Goal**: Project scaffolding, database connection, basic file upload.

- [ ] `docker-compose.yml` with PostgreSQL + pgvector
- [ ] Backend: `pyproject.toml`, FastAPI app factory, config, async database engine
- [ ] Metadata ORM models + initial Alembic migration (3 metadata tables + pgvector extension)
- [ ] Frontend: Vite + React + TypeScript scaffold, Tailwind, Shadcn/ui, TanStack Query
- [ ] `AppShell`, `Header`, `ModeToggle` components
- [ ] Basic file upload endpoint (`POST /api/files/upload`, `GET /api/files`, `DELETE /api/files/{id}`)
- [ ] Frontend `FileUploader` with drag-and-drop

### Phase 2: Spreadsheet Processing

**Goal**: Parse spreadsheets, create dynamic tables, detect relationships.

- [ ] `spreadsheet_processor.py`: pandas parsing, column sanitization, type inference, `CREATE TABLE`, bulk insert
- [ ] `dynamic.py`: utilities for create/drop/introspect dynamic tables
- [ ] `relationship_detector.py`: column name overlap + value overlap verification
- [ ] Frontend `SpreadsheetList` and `RelationshipMap`
- [ ] Wire delete to `DROP TABLE` the dynamic table

### Phase 3: Document Processing

**Goal**: Parse documents, chunk, embed, store in pgvector.

- [ ] `document_processor.py`: PDF (PyMuPDF), DOCX (python-docx), TXT extraction
- [ ] `chunking.py`: 500-token chunks with 50-token overlap
- [ ] Embedding generation with sentence-transformers (lazy singleton model loading)
- [ ] Store chunks + embeddings in `document_chunks`
- [ ] `document_searcher.py`: vector similarity search
- [ ] Frontend `DocumentList`
- [ ] Wire delete to cascade-remove document chunks

### Phase 4: LLM Integration — Query Pipeline

**Goal**: Natural language question answering with Claude.

- [ ] `query_router.py`: build schema context, call Claude to classify question
- [ ] `sql_generator.py`: build detailed schema context with CREATE TABLE + sample data, call Claude for SQL, validate safety, execute read-only
- [ ] Document Q&A flow: retrieve chunks → Claude synthesis
- [ ] Hybrid flow: parallel spreadsheet + document queries → Claude merge
- [ ] `response_formatter.py`: heuristics for display type, format `QueryResponse`
- [ ] `POST /api/query` endpoint

### Phase 5: Frontend — Analyze Mode

**Goal**: Complete query UI with all visualization types.

- [ ] `QueryInput` component (text area, submit, loading state, Ctrl+Enter)
- [ ] `ResultDisplay` router component
- [ ] `DataTable` (sortable, paginated)
- [ ] `ChartDisplay` (Recharts bar/line/pie)
- [ ] `SummaryDisplay` (react-markdown)
- [ ] `QueryHistory` sidebar

### Phase 6: Polish and Error Handling

**Goal**: Robustness, edge cases, UX refinements.

- [ ] Consistent error response format, `ErrorBanner` component
- [ ] File type and size validation (frontend + backend)
- [ ] Loading states: skeleton loaders, progress indicators, spinners
- [ ] SQL safety hardening (statement timeout, row limits)
- [ ] Delete confirmation dialogs
- [ ] Empty states (no files, no relationships)

### Phase 7: Testing and Documentation

**Goal**: Validate with test data, write tests, document setup.

- [ ] Test with provided test data (3 Excel files sharing `program_code`, 1 PDF)
- [ ] Verify relationship detection, cross-referencing queries, document Q&A, hybrid queries
- [ ] Backend unit tests (spreadsheet processor, relationship detector, SQL generator)
- [ ] Integration tests with mocked Claude responses
- [ ] `README.md` with prerequisites, setup instructions, usage guide

---

## 12. Key Architectural Decisions

### pgvector instead of a separate vector database
Keeps everything in PostgreSQL — eliminates a service, simplifies deletion (CASCADE), no sync issues. Sufficient for local-scale document search.

### Two-step LLM pipeline (route then generate)
Separating routing from SQL generation lets each prompt be tightly scoped with only relevant context. Reduces token usage and improves accuracy. Adds ~2-4s latency, acceptable for a local tool.

### Dynamic table creation per spreadsheet (not EAV)
Real PostgreSQL tables mean the LLM generates standard SQL with proper JOINs and aggregations. An Entity-Attribute-Value pattern would make SQL generation far more complex and error-prone.

### Synchronous file processing (no task queue)
For a local single-user app, file processing takes seconds. Adding Celery/Redis would triple infrastructure complexity for negligible benefit.

### Local sentence-transformers instead of API embeddings
`all-MiniLM-L6-v2` is small (80MB), fast, runs on CPU. Avoids burning API tokens on embeddings. Requires `torch` (~2GB with CPU variant) as a trade-off.
