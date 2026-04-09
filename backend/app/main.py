from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
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
