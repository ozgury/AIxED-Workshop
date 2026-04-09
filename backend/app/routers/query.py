import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.query import QueryRequest, QueryResponse
from app.services.document_searcher import search_documents
from app.services.query_router import route_query
from app.services.response_formatter import (
    format_document_response,
    format_hybrid_response,
    format_spreadsheet_response,
)
from app.services.sql_generator import generate_and_execute_sql

router = APIRouter(prefix="/api", tags=["query"])


def _get_embedding_model():
    from app.main import get_embedding_model
    return get_embedding_model()


@router.post("/query", response_model=QueryResponse)
async def submit_query(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db),
):
    if not request.question.strip():
        raise HTTPException(400, "Question cannot be empty")

    routing = await route_query(request.question, db)

    if routing.get("query_type") == "none":
        return QueryResponse(
            answer_text=routing.get("error", "No data available."),
            display_type="summary",
            sources=[],
        )

    query_type = routing["query_type"]
    relevant_tables = routing.get("relevant_tables", [])
    relevant_doc_ids = routing.get("relevant_document_ids", [])
    join_columns = routing.get("join_columns", [])
    sources = []

    if query_type == "spreadsheet":
        sql_result = await generate_and_execute_sql(
            request.question, relevant_tables, join_columns
        )
        sources = relevant_tables
        return await format_spreadsheet_response(request.question, sql_result, sources)

    elif query_type == "document":
        embedding_model = _get_embedding_model()
        chunks = await search_documents(
            request.question, embedding_model, db, relevant_doc_ids
        )
        sources = list({c["source"] for c in chunks})
        return await format_document_response(request.question, chunks, sources)

    elif query_type == "hybrid":
        embedding_model = _get_embedding_model()

        sql_task = generate_and_execute_sql(
            request.question, relevant_tables, join_columns
        )
        doc_task = search_documents(
            request.question, embedding_model, db, relevant_doc_ids
        )

        sql_result, chunks = await asyncio.gather(sql_task, doc_task)
        sources = relevant_tables + list({c["source"] for c in chunks})
        return await format_hybrid_response(
            request.question, sql_result, chunks, sources
        )

    else:
        raise HTTPException(500, f"Unknown query type: {query_type}")
