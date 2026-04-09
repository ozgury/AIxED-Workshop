import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def search_documents(
    question: str,
    embedding_model,
    db: AsyncSession,
    file_ids: list[str] | None = None,
    limit: int = 10,
) -> list[dict]:
    query_embedding = embedding_model.encode(question).tolist()

    if file_ids:
        placeholders = ", ".join(f":fid_{i}" for i in range(len(file_ids)))
        sql = text(
            f"SELECT dc.content, dc.metadata, dc.file_id, uf.original_name, "
            f"dc.embedding <=> :embedding AS distance "
            f"FROM document_chunks dc "
            f"JOIN uploaded_files uf ON dc.file_id = uf.id "
            f"WHERE dc.file_id IN ({placeholders}) "
            f"ORDER BY dc.embedding <=> :embedding "
            f"LIMIT :lim"
        )
        params = {"embedding": str(query_embedding), "lim": limit}
        for i, fid in enumerate(file_ids):
            params[f"fid_{i}"] = fid
    else:
        sql = text(
            "SELECT dc.content, dc.metadata, dc.file_id, uf.original_name, "
            "dc.embedding <=> :embedding AS distance "
            "FROM document_chunks dc "
            "JOIN uploaded_files uf ON dc.file_id = uf.id "
            "ORDER BY dc.embedding <=> :embedding "
            "LIMIT :lim"
        )
        params = {"embedding": str(query_embedding), "lim": limit}

    result = await db.execute(sql, params)
    rows = result.fetchall()

    return [
        {
            "content": row[0],
            "metadata": row[1],
            "file_id": str(row[2]),
            "source": row[3],
            "distance": float(row[4]),
        }
        for row in rows
    ]
