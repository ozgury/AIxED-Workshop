from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.metadata import ColumnRelationship, UploadedFile
from app.schemas.relationships import RelationshipListResponse, RelationshipResponse

router = APIRouter(prefix="/api", tags=["schema"])


@router.get("/relationships", response_model=RelationshipListResponse)
async def list_relationships(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ColumnRelationship))
    rels = result.scalars().all()
    return RelationshipListResponse(
        relationships=[
            RelationshipResponse(
                id=r.id,
                column_name=r.column_name,
                table_names=r.table_names,
                file_ids=[str(fid) for fid in r.file_ids],
                detected_at=r.detected_at,
            )
            for r in rels
        ]
    )


@router.get("/schema")
async def get_schema(db: AsyncSession = Depends(get_db)):
    files_result = await db.execute(
        select(UploadedFile).where(UploadedFile.status == "ready")
    )
    files = files_result.scalars().all()

    rels_result = await db.execute(select(ColumnRelationship))
    rels = rels_result.scalars().all()

    return {
        "spreadsheets": [
            {
                "table_name": f.table_name,
                "original_name": f.original_name,
                "columns": f.column_names,
                "row_count": f.row_count,
            }
            for f in files
            if f.file_type == "spreadsheet"
        ],
        "documents": [
            {
                "file_id": str(f.id),
                "original_name": f.original_name,
                "mime_type": f.mime_type,
            }
            for f in files
            if f.file_type == "document"
        ],
        "relationships": [
            {
                "column_name": r.column_name,
                "table_names": r.table_names,
            }
            for r in rels
        ],
    }
