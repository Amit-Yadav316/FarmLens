from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from farmlens.core.exceptions import FarmLensException
from farmlens.features.asr.exceptions import ASRException
from farmlens.features.mandi.exceptions import MandiException
from farmlens.features.rag.exceptions import RAGException
from farmlens.features.weather.exceptions import WeatherException

# Map domain exceptions to HTTP status codes.
# 502: an upstream third-party API failed. 503: a local dependency
# (Ollama, Whisper) is unavailable. Everything else falls back to 500.
_STATUS_MAP: dict[type[FarmLensException], int] = {
    MandiException: 502,
    WeatherException: 502,
    RAGException: 503,
    ASRException: 503,
}


def _handle_farmlens_exception(request: Request, exc: Exception) -> JSONResponse:
    """Convert a FarmLens domain exception into a clean JSON error response."""
    status_code = 500
    if isinstance(exc, FarmLensException):
        status_code = _STATUS_MAP.get(type(exc), 500)
    return JSONResponse(
        status_code=status_code,
        content={"detail": str(exc), "error": type(exc).__name__},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register handlers that translate domain exceptions to HTTP responses."""
    app.add_exception_handler(FarmLensException, _handle_farmlens_exception)
