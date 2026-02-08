"""RAG Chat API endpoints."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
import json

from ..services.rag_service import rag_service

router = APIRouter()


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    session_id: Optional[str] = None
    selected_context: Optional[str] = Field(None, max_length=2000)


@router.post("")
async def chat_global(request: ChatRequest):
    """Global book Q&A — searches entire textbook corpus."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    async def generate():
        async for event in rag_service.query(
            query=request.query,
            selected_context=request.selected_context,
        ):
            yield json.dumps(event) + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")


@router.post("/chapter/{chapter_slug}")
async def chat_chapter_scoped(chapter_slug: str, request: ChatRequest):
    """Chapter-scoped Q&A — only searches the specified chapter."""
    valid_slugs = [
        "ch01-intro-physical-ai",
        "ch02-ros2-fundamentals",
        "ch03-digital-twin",
        "ch04-isaac-platform",
        "ch05-vla",
        "ch06-capstone",
    ]
    if chapter_slug not in valid_slugs:
        raise HTTPException(status_code=404, detail=f"Chapter '{chapter_slug}' not found")

    async def generate():
        async for event in rag_service.query(
            query=request.query,
            chapter_slug=chapter_slug,
            selected_context=request.selected_context,
        ):
            yield json.dumps(event) + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")
