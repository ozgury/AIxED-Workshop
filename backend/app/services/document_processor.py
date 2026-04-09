import uuid
from pathlib import Path

from app.utils.chunking import chunk_text


def extract_text_from_pdf(file_path: Path) -> str:
    import fitz

    doc = fitz.open(str(file_path))
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return "\n\n".join(pages)


def extract_text_from_docx(file_path: Path) -> str:
    from docx import Document

    doc = Document(str(file_path))
    return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())


def extract_text_from_txt(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8", errors="replace")


def extract_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(file_path)
    elif suffix in (".docx", ".doc"):
        return extract_text_from_docx(file_path)
    elif suffix == ".txt":
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported document format: {suffix}")


async def process_document(
    file_path: Path,
    file_id: uuid.UUID,
    db_session,
    embedding_model,
) -> dict:
    from sqlalchemy import text as sql_text

    full_text = extract_text(file_path)
    chunks = chunk_text(full_text)

    if not chunks:
        return {"chunk_count": 0}

    embeddings = embedding_model.encode(chunks, show_progress_bar=False)

    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        await db_session.execute(
            sql_text(
                "INSERT INTO document_chunks (id, file_id, chunk_index, content, embedding, metadata) "
                "VALUES (gen_random_uuid(), :file_id, :idx, :content, :embedding, :meta)"
            ),
            {
                "file_id": file_id,
                "idx": i,
                "content": chunk,
                "embedding": embedding.tolist(),
                "meta": {"chunk_index": i, "total_chunks": len(chunks)},
            },
        )
    await db_session.commit()

    return {"chunk_count": len(chunks)}
