from __future__ import annotations

from pydantic import BaseModel


class RAGRequest(BaseModel):
    """Request model for a RAG-based farming question."""

    question: str
    language: str = "hi"
    top_k: int = 3


class SourceDocument(BaseModel):
    """A source document chunk returned alongside an answer."""

    content: str
    source: str
    page: int | None = None


class RAGResponse(BaseModel):
    """Response model for a RAG-based farming question."""

    answer: str
    sources: list[SourceDocument]
    language: str
