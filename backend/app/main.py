import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings

_embedding_model = None


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        _embedding_model = SentenceTransformer(settings.embedding_model)
    return _embedding_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.database import async_engine, Base
    from app.models.metadata import UploadedFile, ColumnRelationship, DocumentChunk  # noqa: F401
    from sqlalchemy import text

    async with async_engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)

    yield

    await async_engine.dispose()


app = FastAPI(
    title="WildCard",
    description="Natural language data exploration",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import files, query, schema  # noqa: E402

app.include_router(files.router)
app.include_router(query.router)
app.include_router(schema.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# Serve frontend — try pre-built dist, fall back to inline HTML
_frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

# Debug endpoint
@app.get("/api/debug")
async def debug():
    return {
        "frontend_dist": str(_frontend_dist),
        "exists": _frontend_dist.is_dir(),
        "contents": os.listdir(_frontend_dist) if _frontend_dist.is_dir() else [],
    }


if _frontend_dist.is_dir():
    from fastapi.responses import FileResponse

    if (_frontend_dist / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=_frontend_dist / "assets"), name="assets")

    @app.get("/", response_class=HTMLResponse)
    async def serve_index():
        return FileResponse(_frontend_dist / "index.html")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = _frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(_frontend_dist / "index.html")
else:
    @app.get("/", response_class=HTMLResponse)
    async def fallback_index():
        return """<!DOCTYPE html>
<html><head><title>WildCard</title></head>
<body style="font-family:sans-serif;max-width:600px;margin:50px auto;text-align:center">
<h1>WildCard</h1>
<p>Backend is running but frontend dist not found.</p>
<p>Expected at: """ + str(_frontend_dist) + """</p>
<p><a href="/api/health">Check API health</a></p>
</body></html>"""
