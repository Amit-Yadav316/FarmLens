from __future__ import annotations

from fastapi import APIRouter, Depends, UploadFile

from farmlens.core.dependencies import get_asr_service, get_intent_router, get_rag_pipeline
from farmlens.features.asr.service import ASRService
from farmlens.features.intent.router import IntentRouter
from farmlens.features.rag.pipeline import RAGPipeline
from farmlens.features.rag.schemas import RAGResponse

router = APIRouter()


def _ensure_ready(pipeline: RAGPipeline) -> None:
    """Initialize the RAG pipeline on first use."""
    if not pipeline.is_ready:
        pipeline.initialize()


@router.post("/chat", response_model=RAGResponse)
async def chat(
    question: str,
    language: str = "hi",
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
    intent_router: IntentRouter = Depends(get_intent_router),
) -> RAGResponse:
    """Classify a text farming question and answer it via RAG."""
    intent_router.classify(question)
    _ensure_ready(pipeline)
    return pipeline.answer(question, language)


@router.post("/voice-chat", response_model=RAGResponse)
async def voice_chat(
    audio: UploadFile,
    language: str = "hi",
    asr: ASRService = Depends(get_asr_service),
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
    intent_router: IntentRouter = Depends(get_intent_router),
) -> RAGResponse:
    """Transcribe audio, classify the question, and answer it via RAG."""
    audio_bytes = await audio.read()
    transcript = asr.transcribe(audio_bytes, language)
    intent_router.classify(transcript.text)
    _ensure_ready(pipeline)
    return pipeline.answer(transcript.text, language)
