import json
import re

import anthropic
from sqlalchemy import text

from app.config import settings
from app.database import async_engine
from app.models.dynamic import get_create_table_ddl, get_sample_rows

DANGEROUS_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|GRANT|REVOKE|COPY|EXECUTE)\b"
    r"|DO\s*\$\$|pg_",
    re.IGNORECASE,
)


async def generate_and_execute_sql(
    question: str,
    relevant_tables: list[str],
    join_columns: list[str],
) -> dict:
    schema_parts = []
    sample_parts = []

    for table_name in relevant_tables:
        ddl = await get_create_table_ddl(table_name)
        if ddl:
            schema_parts.append(ddl)
        samples = await get_sample_rows(table_name, limit=3)
        if samples:
            sample_parts.append(f"Sample from {table_name}: {json.dumps(samples, default=str)}")

    if not schema_parts:
        return {"error": "No table schemas found", "rows": [], "columns": []}

    schema_context = "\n".join(schema_parts)
    samples_context = "\n".join(sample_parts) if sample_parts else "No sample data."

    join_context = ""
    if join_columns:
        join_context = f"\nThese tables can be joined on: {', '.join(join_columns)}"

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    system_prompt = (
        "You are a PostgreSQL SQL expert. Generate a single SELECT query to answer "
        "the user's question. Use ONLY the tables and columns provided. "
        "Return ONLY valid JSON with 'sql' and 'explanation' fields. No markdown.\n\n"
        "Rules:\n"
        "- Only generate SELECT statements\n"
        "- NEVER generate INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, or any DDL\n"
        "- Always quote table and column names with double quotes\n"
        "- Use appropriate aggregations, JOINs, and filtering\n"
        "- If the question asks about trends over time, ORDER BY the time column\n"
        "- Limit results to 1000 rows maximum"
    )

    user_content = (
        f"Table schemas:\n{schema_context}\n\n"
        f"Sample data:\n{samples_context}\n"
        f"{join_context}\n\n"
        f"Question: {question}"
    )

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )

    try:
        result = json.loads(response.content[0].text)
        sql = result["sql"]
        explanation = result.get("explanation", "")
    except (json.JSONDecodeError, KeyError):
        raw = response.content[0].text
        sql_match = re.search(r"(?:```sql\s*)?(SELECT.+?)(?:```|$)", raw, re.DOTALL | re.IGNORECASE)
        if sql_match:
            sql = sql_match.group(1).strip()
            explanation = "Query extracted from response."
        else:
            return {"error": "Could not generate SQL", "rows": [], "columns": []}

    if DANGEROUS_KEYWORDS.search(sql):
        return {"error": "Generated SQL contains unsafe operations", "rows": [], "columns": []}

    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SET statement_timeout = '30s'"))
            await conn.execute(text("SET TRANSACTION READ ONLY"))
            result = await conn.execute(text(sql))
            rows = result.fetchall()
            columns = list(result.keys())
            await conn.rollback()

        row_dicts = [dict(zip(columns, row)) for row in rows]

        return {
            "sql": sql,
            "explanation": explanation,
            "columns": columns,
            "rows": row_dicts,
        }
    except Exception as e:
        return {
            "sql": sql,
            "error": f"SQL execution error: {str(e)}",
            "columns": [],
            "rows": [],
        }
