import json

import anthropic

from app.config import settings
from app.schemas.query import ChartData, ChartDataset, QueryResponse, TableData


def _is_numeric(val) -> bool:
    if val is None:
        return False
    try:
        float(val)
        return True
    except (ValueError, TypeError):
        return False


def _detect_display_type(columns: list[str], rows: list[dict]) -> str:
    if not rows or not columns:
        return "summary"

    if len(rows) == 1 and len(columns) == 1:
        return "summary"

    numeric_cols = []
    text_cols = []
    for col in columns:
        sample_vals = [r.get(col) for r in rows[:10] if r.get(col) is not None]
        if sample_vals and all(_is_numeric(v) for v in sample_vals):
            numeric_cols.append(col)
        else:
            text_cols.append(col)

    # Time series detection
    time_keywords = {"year", "term", "semester", "date", "month", "quarter", "period"}
    has_time_col = any(
        any(kw in col.lower() for kw in time_keywords)
        for col in text_cols + numeric_cols
    )

    if has_time_col and numeric_cols and len(rows) >= 2:
        return "line_chart"

    if len(text_cols) == 1 and len(numeric_cols) >= 1:
        if len(rows) <= 8:
            return "pie_chart"
        if len(rows) <= 30:
            return "bar_chart"

    if len(rows) > 1:
        return "table"

    return "summary"


def _build_chart_data(
    columns: list[str], rows: list[dict], chart_type: str
) -> ChartData | None:
    if not rows or not columns:
        return None

    numeric_cols = []
    label_col = None

    for col in columns:
        sample = [r.get(col) for r in rows[:10] if r.get(col) is not None]
        if sample and all(_is_numeric(v) for v in sample):
            numeric_cols.append(col)
        elif label_col is None:
            label_col = col

    if not label_col and columns:
        label_col = columns[0]
    if not numeric_cols:
        return None

    labels = [str(r.get(label_col, "")) for r in rows]
    datasets = []
    for nc in numeric_cols:
        data = []
        for r in rows:
            val = r.get(nc)
            try:
                data.append(float(val) if val is not None else None)
            except (ValueError, TypeError):
                data.append(None)
        datasets.append(ChartDataset(label=nc, data=data))

    return ChartData(
        labels=labels,
        datasets=datasets,
        chart_type=chart_type.replace("_chart", ""),
    )


def _build_table_data(columns: list[str], rows: list[dict]) -> TableData | None:
    if not rows:
        return None
    row_lists = []
    for r in rows:
        row_lists.append([r.get(c) for c in columns])
    return TableData(columns=columns, rows=row_lists)


async def format_spreadsheet_response(
    question: str,
    sql_result: dict,
    sources: list[str],
) -> QueryResponse:
    columns = sql_result.get("columns", [])
    rows = sql_result.get("rows", [])
    sql_used = sql_result.get("sql")
    explanation = sql_result.get("explanation", "")

    if sql_result.get("error"):
        return QueryResponse(
            answer_text=f"I encountered an issue: {sql_result['error']}",
            display_type="summary",
            sources=sources,
            sql_used=sql_used,
        )

    display_type = _detect_display_type(columns, rows)

    # Generate natural language answer
    answer_text = await _generate_answer_text(question, columns, rows, explanation)

    table_data = _build_table_data(columns, rows) if display_type == "table" else None
    chart_data = _build_chart_data(columns, rows, display_type) if "chart" in display_type else None

    # Also include table for charts
    if chart_data and not table_data:
        table_data = _build_table_data(columns, rows)

    return QueryResponse(
        answer_text=answer_text,
        display_type=display_type,
        table_data=table_data,
        chart_data=chart_data,
        sql_used=sql_used,
        sources=sources,
    )


async def format_document_response(
    question: str,
    chunks: list[dict],
    sources: list[str],
) -> QueryResponse:
    if not chunks:
        return QueryResponse(
            answer_text="I couldn't find relevant information in the uploaded documents.",
            display_type="summary",
            sources=sources,
        )

    context = "\n\n".join(
        f"[From {c['source']}]:\n{c['content']}" for c in chunks
    )

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=(
            "Answer the user's question using ONLY the provided document excerpts. "
            "Cite which document each piece of information comes from. "
            "Format your answer in clear markdown."
        ),
        messages=[{
            "role": "user",
            "content": f"Document excerpts:\n{context}\n\nQuestion: {question}",
        }],
    )

    return QueryResponse(
        answer_text=response.content[0].text,
        display_type="summary",
        sources=sources,
    )


async def format_hybrid_response(
    question: str,
    sql_result: dict,
    chunks: list[dict],
    sources: list[str],
) -> QueryResponse:
    data_summary = ""
    columns = sql_result.get("columns", [])
    rows = sql_result.get("rows", [])

    if rows and not sql_result.get("error"):
        data_summary = f"Structured data ({len(rows)} rows):\n"
        data_summary += json.dumps(rows[:20], default=str, indent=2)

    doc_context = ""
    if chunks:
        doc_context = "\n\n".join(
            f"[From {c['source']}]:\n{c['content']}" for c in chunks
        )

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=(
            "Combine the structured data results and document excerpts to answer "
            "the user's question comprehensively. Reference specific data points and "
            "document sources. Format in clear markdown."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Structured data:\n{data_summary}\n\n"
                f"Document excerpts:\n{doc_context}\n\n"
                f"Question: {question}"
            ),
        }],
    )

    display_type = _detect_display_type(columns, rows) if rows else "summary"
    table_data = _build_table_data(columns, rows) if rows and display_type == "table" else None
    chart_data = _build_chart_data(columns, rows, display_type) if rows and "chart" in display_type else None

    return QueryResponse(
        answer_text=response.content[0].text,
        display_type=display_type if rows else "summary",
        table_data=table_data,
        chart_data=chart_data,
        sql_used=sql_result.get("sql"),
        sources=sources,
    )


async def _generate_answer_text(
    question: str, columns: list[str], rows: list[dict], explanation: str
) -> str:
    if not rows:
        return "The query returned no results."

    if len(rows) == 1 and len(columns) == 1:
        val = list(rows[0].values())[0]
        return f"The answer is **{val}**."

    data_preview = json.dumps(rows[:15], default=str)

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=(
            "Provide a concise natural language summary of the data results that answers "
            "the user's question. Use markdown formatting. Be specific with numbers."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Question: {question}\n\n"
                f"Query explanation: {explanation}\n\n"
                f"Results ({len(rows)} rows):\n{data_preview}"
            ),
        }],
    )
    return response.content[0].text
