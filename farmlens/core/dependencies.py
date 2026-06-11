from __future__ import annotations

from fastapi import Depends

from farmlens.core.config import Settings, get_settings
from farmlens.features.asr.service import ASRService
from farmlens.features.intent.router import IntentRouter
from farmlens.features.mandi.service import MandiService
from farmlens.features.rag.pipeline import RAGPipeline
from farmlens.features.schemes.service import SchemeService
from farmlens.features.weather.service import WeatherService


def get_mandi_service(
    settings: Settings = Depends(get_settings),
) -> MandiService:
    """Provide a MandiService instance."""
    return MandiService(settings)


def get_weather_service(
    settings: Settings = Depends(get_settings),
) -> WeatherService:
    """Provide a WeatherService instance."""
    return WeatherService(settings)


def get_asr_service() -> ASRService:
    """Provide an ASRService instance."""
    return ASRService()


def get_scheme_service() -> SchemeService:
    """Provide a SchemeService instance."""
    return SchemeService()


_rag_pipeline: RAGPipeline | None = None


def get_rag_pipeline(
    settings: Settings = Depends(get_settings),
) -> RAGPipeline:
    """Provide the shared RAGPipeline singleton (one instance per app)."""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline(settings)
    return _rag_pipeline


def get_intent_router() -> IntentRouter:
    """Provide an IntentRouter instance."""
    return IntentRouter()
