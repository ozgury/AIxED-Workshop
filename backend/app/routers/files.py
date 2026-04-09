import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.dynamic import drop_dynamic_table
from app.models.metadata import UploadedFile
from app.schemas.files import FileListResponse, FileResponse
from app.services.file_processor import classify_file, process_file
from app.services.relationship_detector import cleanup_relationships_for_file, detect_relationships

router = APIRouter(prefix="/api/files", tags=["files"])


def _get_embedding_model():
    from app.main import get_embedding_model
    return get_embedding_model()


@router.post("/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(400, "No filename provided")

    try:
        file_type = classify_file(file.filename, file.content_type or "")
    except ValueError as e:
        raise HTTPException(400, str(e))

    content = await file.read()
    if len(content) > settings.max_file_size_bytes:
        raise HTTPException(400, f"File exceeds {settings.max_file_size_mb}MB limit")

    file_id = uuid.uuid4()
    ext = os.path.splitext(file.filename)[1]
    stored_filename = f"{file_id}{ext}"
    stored_path = settings.upload_path / stored_filename

    with open(stored_path, "wb") as f:
        f.write(content)

    db_file = UploadedFile(
        id=file_id,
        original_name=file.filename,
        stored_path=str(stored_path),
        file_type=file_type,
        mime_type=file.content_type or "application/octet-stream",
        file_size=len(content),
        status="processing",
    )
    db.add(db_file)
    await db.commit()

    try:
        embedding_model = _get_embedding_model() if file_type == "document" else None
        result = await process_file(
            stored_path, file_id, file_type, db, embedding_model
        )

        db_file.status = "ready"
        if file_type == "spreadsheet":
            db_file.table_name = result["table_name"]
            db_file.row_count = result["row_count"]
            db_file.column_names = result["column_names"]

        await db.commit()

        if file_type == "spreadsheet":
            await detect_relationships(db)

    except Exception as e:
        db_file.status = "error"
        db_file.error_message = str(e)
        await db.commit()
        raise HTTPException(500, f"Error processing file: {e}")

    await db.refresh(db_file)
    return db_file


@router.get("", response_model=FileListResponse)
async def list_files(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UploadedFile).order_by(UploadedFile.created_at.desc())
    )
    files = result.scalars().all()
    return FileListResponse(files=files, total=len(files))


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(file_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UploadedFile).where(UploadedFile.id == file_id)
    )
    file = result.scalar_one_or_none()
    if not file:
        raise HTTPException(404, "File not found")
    return file


@router.delete("/{file_id}")
async def delete_file(file_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UploadedFile).where(UploadedFile.id == file_id)
    )
    file = result.scalar_one_or_none()
    if not file:
        raise HTTPException(404, "File not found")

    if file.file_type == "spreadsheet" and file.table_name:
        await drop_dynamic_table(file.table_name)
        await cleanup_relationships_for_file(db, str(file.id))

    if os.path.exists(file.stored_path):
        os.remove(file.stored_path)

    await db.delete(file)
    await db.commit()

    return {"status": "deleted", "id": str(file_id)}
