from __future__ import annotations

from fastapi import APIRouter, Depends, UploadFile

from farmlens.core.dependencies import get_asr_service, get_intent_router, get_rag_pipeline
from farmlens.features.asr.service import ASRService
from farmlens.features.intent.router import IntentRouter
from farmlens.features.rag.pipeline import RAGPipeline
from farmlens.features.rag.schemas import RAGResponse

router = APIRouter()


@router.post("/chat", response_model=RAGResponse)
async def chat(
    question: str,
    language: str = "hi",
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
    intent_router: IntentRouter = Depends(get_intent_router),
) -> RAGResponse:
    """Answer a text farming question."""
    raise NotImplementedError


@router.post("/voice-chat", response_model=RAGResponse)
async def voice_chat(
    audio: UploadFile,
    language: str = "hi",
    asr: ASRService = Depends(get_asr_service),
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
    intent_router: IntentRouter = Depends(get_intent_router),
) -> RAGResponse:
    """Transcribe audio and answer the farming question."""
    raise NotImplementedError
