import uuid
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from app.database import async_engine
from app.models.dynamic import create_dynamic_table
from app.utils.sanitization import deduplicate_columns, sanitize_column_name, sanitize_table_name
from app.utils.type_inference import clean_value, pandas_dtype_to_sqlalchemy


async def process_spreadsheet(file_path: Path, file_id: uuid.UUID) -> dict:
    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(file_path)
    elif suffix in (".xlsx", ".xls"):
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported spreadsheet format: {suffix}")

    raw_columns = [sanitize_column_name(str(c)) for c in df.columns]
    sanitized_columns = deduplicate_columns(raw_columns)
    df.columns = sanitized_columns

    file_id_short = str(file_id).replace("-", "")[:8]
    table_name = sanitize_table_name(file_id_short, file_path.name)

    sa_columns = []
    for col_name in sanitized_columns:
        sa_col = pandas_dtype_to_sqlalchemy(df[col_name].dtype, col_name)
        sa_columns.append(sa_col)

    await create_dynamic_table(table_name, sa_columns)

    rows = df.where(df.notna(), None).to_dict("records")
    cleaned_rows = []
    for row in rows:
        cleaned_rows.append({k: clean_value(v) for k, v in row.items()})

    if cleaned_rows:
        batch_size = 500
        for i in range(0, len(cleaned_rows), batch_size):
            batch = cleaned_rows[i : i + batch_size]
            col_names = ", ".join(f'"{c}"' for c in sanitized_columns)
            placeholders = ", ".join(
                "(" + ", ".join(f":{c}_{j}" for c in sanitized_columns) + ")"
                for j in range(len(batch))
            )
            params = {}
            for j, row in enumerate(batch):
                for c in sanitized_columns:
                    params[f"{c}_{j}"] = row.get(c)

            sql = f'INSERT INTO "{table_name}" ({col_names}) VALUES {placeholders}'
            async with async_engine.begin() as conn:
                await conn.execute(text(sql), params)

    return {
        "table_name": table_name,
        "row_count": len(df),
        "column_names": sanitized_columns,
    }
