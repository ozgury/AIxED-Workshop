import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document_processor import process_document
from app.services.spreadsheet_processor import process_spreadsheet

SPREADSHEET_EXTENSIONS = {".csv", ".xlsx", ".xls"}
DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}
SPREADSHEET_MIMES = {
    "text/csv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
DOCUMENT_MIMES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "text/plain",
}


def classify_file(filename: str, mime_type: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext in SPREADSHEET_EXTENSIONS:
        return "spreadsheet"
    if ext in DOCUMENT_EXTENSIONS:
        return "document"
    if mime_type in SPREADSHEET_MIMES:
        return "spreadsheet"
    if mime_type in DOCUMENT_MIMES:
        return "document"
    raise ValueError(f"Unsupported file type: {filename} ({mime_type})")


async def process_file(
    file_path: Path,
    file_id: uuid.UUID,
    file_type: str,
    db: AsyncSession,
    embedding_model=None,
) -> dict:
    if file_type == "spreadsheet":
        return await process_spreadsheet(file_path, file_id)
    elif file_type == "document":
        if embedding_model is None:
            raise RuntimeError("Embedding model required for document processing")
        return await process_document(file_path, file_id, db, embedding_model)
    else:
        raise ValueError(f"Unknown file type: {file_type}")
