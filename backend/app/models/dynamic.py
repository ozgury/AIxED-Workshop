from sqlalchemy import Column, Integer, MetaData, Table, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_engine


async def create_dynamic_table(
    table_name: str, columns: list[Column]
) -> Table:
    metadata = MetaData()
    all_columns = [
        Column("_wc_row_id", Integer, primary_key=True, autoincrement=True),
        *columns,
    ]
    table = Table(table_name, metadata, *all_columns)
    async with async_engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    return table


async def drop_dynamic_table(table_name: str) -> None:
    async with async_engine.begin() as conn:
        await conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}" CASCADE'))


async def get_table_columns(table_name: str) -> list[dict]:
    async with async_engine.connect() as conn:
        result = await conn.execute(
            text(
                "SELECT column_name, data_type "
                "FROM information_schema.columns "
                "WHERE table_name = :table_name AND column_name != '_wc_row_id' "
                "ORDER BY ordinal_position"
            ),
            {"table_name": table_name},
        )
        return [{"name": row[0], "type": row[1]} for row in result.fetchall()]


async def get_create_table_ddl(table_name: str) -> str:
    columns = await get_table_columns(table_name)
    if not columns:
        return ""
    col_defs = ", ".join(f'"{c["name"]}" {c["type"].upper()}' for c in columns)
    return f'CREATE TABLE "{table_name}" ({col_defs});'


async def get_sample_rows(table_name: str, limit: int = 3) -> list[dict]:
    async with async_engine.connect() as conn:
        cols = await get_table_columns(table_name)
        col_names = [c["name"] for c in cols]
        if not col_names:
            return []
        select_cols = ", ".join(f'"{c}"' for c in col_names)
        result = await conn.execute(
            text(f'SELECT {select_cols} FROM "{table_name}" LIMIT {limit}')
        )
        rows = result.fetchall()
        return [dict(zip(col_names, row)) for row in rows]
