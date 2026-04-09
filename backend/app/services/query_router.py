import json

import anthropic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.metadata import ColumnRelationship, UploadedFile


async def build_schema_context(db: AsyncSession) -> dict:
    files_result = await db.execute(
        select(UploadedFile).where(UploadedFile.status == "ready")
    )
    files = files_result.scalars().all()

    rels_result = await db.execute(select(ColumnRelationship))
    relationships = rels_result.scalars().all()

    spreadsheets = []
    documents = []
    for f in files:
        if f.file_type == "spreadsheet":
            spreadsheets.append({
                "table_name": f.table_name,
                "original_name": f.original_name,
                "columns": f.column_names or [],
                "row_count": f.row_count or 0,
            })
        else:
            documents.append({
                "file_id": str(f.id),
                "original_name": f.original_name,
                "mime_type": f.mime_type,
            })

    rels = [
        {
            "column_name": r.column_name,
            "table_names": r.table_names,
        }
        for r in relationships
    ]

    return {
        "spreadsheets": spreadsheets,
        "documents": documents,
        "relationships": rels,
    }


async def route_query(question: str, db: AsyncSession) -> dict:
    context = await build_schema_context(db)

    if not context["spreadsheets"] and not context["documents"]:
        return {
            "query_type": "none",
            "error": "No data has been uploaded yet.",
        }

    if not context["spreadsheets"]:
        return {
            "query_type": "document",
            "relevant_tables": [],
            "relevant_documents": [d["original_name"] for d in context["documents"]],
            "relevant_document_ids": [d["file_id"] for d in context["documents"]],
            "needs_join": False,
            "join_columns": [],
        }

    if not context["documents"]:
        all_tables = [s["table_name"] for s in context["spreadsheets"]]
        return {
            "query_type": "spreadsheet",
            "relevant_tables": all_tables,
            "relevant_documents": [],
            "relevant_document_ids": [],
            "needs_join": len(all_tables) > 1 and len(context["relationships"]) > 0,
            "join_columns": [r["column_name"] for r in context["relationships"]],
        }

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    system_prompt = (
        "You are a query classifier. Given a user question and available data sources, "
        "determine which sources to query. Respond with ONLY valid JSON, no markdown.\n\n"
        "Output format:\n"
        '{"query_type": "spreadsheet"|"document"|"hybrid", '
        '"relevant_tables": ["table_name1"], '
        '"relevant_documents": ["filename.pdf"], '
        '"needs_join": true/false, '
        '"join_columns": ["col_name"]}'
    )

    user_content = (
        f"Available data:\n\n"
        f"Spreadsheets:\n{json.dumps(context['spreadsheets'], indent=2)}\n\n"
        f"Documents:\n{json.dumps(context['documents'], indent=2)}\n\n"
        f"Relationships (shared columns):\n{json.dumps(context['relationships'], indent=2)}\n\n"
        f"User question: {question}"
    )

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )

    try:
        result = json.loads(response.content[0].text)
    except (json.JSONDecodeError, IndexError):
        # Fallback: query everything
        result = {
            "query_type": "hybrid",
            "relevant_tables": [s["table_name"] for s in context["spreadsheets"]],
            "relevant_documents": [d["original_name"] for d in context["documents"]],
            "needs_join": len(context["relationships"]) > 0,
            "join_columns": [r["column_name"] for r in context["relationships"]],
        }

    # Enrich with document file_ids
    doc_name_to_id = {d["original_name"]: d["file_id"] for d in context["documents"]}
    result["relevant_document_ids"] = [
        doc_name_to_id[name]
        for name in result.get("relevant_documents", [])
        if name in doc_name_to_id
    ]

    return result
