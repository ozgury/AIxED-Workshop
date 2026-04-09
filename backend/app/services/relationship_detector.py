import uuid
from collections import defaultdict

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_engine
from app.models.metadata import ColumnRelationship, UploadedFile


async def detect_relationships(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(UploadedFile).where(
            UploadedFile.file_type == "spreadsheet",
            UploadedFile.status == "ready",
        )
    )
    files = result.scalars().all()

    if len(files) < 2:
        return []

    column_to_tables: dict[str, list[dict]] = defaultdict(list)
    for f in files:
        if f.column_names:
            for col in f.column_names:
                column_to_tables[col].append({
                    "table_name": f.table_name,
                    "file_id": str(f.id),
                    "original_name": f.original_name,
                })

    shared_columns = {
        col: entries for col, entries in column_to_tables.items()
        if len(entries) >= 2
    }

    relationships = []
    for col_name, entries in shared_columns.items():
        table_names = [e["table_name"] for e in entries]
        file_ids = [e["file_id"] for e in entries]

        # Verify value overlap between first two tables
        verified = await _verify_value_overlap(table_names[0], table_names[1], col_name)
        if not verified:
            continue

        existing = await db.execute(
            select(ColumnRelationship).where(
                ColumnRelationship.column_name == col_name
            )
        )
        rel = existing.scalar_one_or_none()

        if rel:
            rel.table_names = table_names
            rel.file_ids = file_ids
        else:
            rel = ColumnRelationship(
                column_name=col_name,
                table_names=table_names,
                file_ids=file_ids,
            )
            db.add(rel)

        relationships.append({
            "column_name": col_name,
            "table_names": table_names,
            "file_ids": file_ids,
        })

    await db.commit()
    return relationships


async def _verify_value_overlap(
    table1: str, table2: str, column: str
) -> bool:
    try:
        async with async_engine.connect() as conn:
            r1 = await conn.execute(
                text(f'SELECT DISTINCT "{column}" FROM "{table1}" WHERE "{column}" IS NOT NULL LIMIT 20')
            )
            vals1 = {row[0] for row in r1.fetchall()}

            r2 = await conn.execute(
                text(f'SELECT DISTINCT "{column}" FROM "{table2}" WHERE "{column}" IS NOT NULL LIMIT 20')
            )
            vals2 = {row[0] for row in r2.fetchall()}

            # Convert to strings for comparison across types
            str_vals1 = {str(v) for v in vals1}
            str_vals2 = {str(v) for v in vals2}

            return len(str_vals1 & str_vals2) > 0
    except Exception:
        return False


async def cleanup_relationships_for_file(db: AsyncSession, file_id: str) -> None:
    result = await db.execute(select(ColumnRelationship))
    rels = result.scalars().all()

    for rel in rels:
        if file_id in rel.file_ids:
            new_file_ids = [fid for fid in rel.file_ids if fid != file_id]
            new_table_names = [
                tn for tn, fid in zip(rel.table_names, rel.file_ids)
                if fid != file_id
            ]
            if len(new_file_ids) < 2:
                await db.delete(rel)
            else:
                rel.file_ids = new_file_ids
                rel.table_names = new_table_names

    await db.commit()
