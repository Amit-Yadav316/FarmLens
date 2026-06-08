from __future__ import annotations

from pydantic import BaseModel


class TranscriptRequest(BaseModel):
    """Request model for ASR transcription."""

    language: str = "hi"


class TranscriptResponse(BaseModel):
    """Response model for ASR transcription."""

    text: str
    language: str
    confidence: float | None = None
