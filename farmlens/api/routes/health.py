from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Response model for health check endpoints."""

    status: str
    version: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return service health status."""
    return HealthResponse(status="ok", version="0.1.0")


@router.get("/status", response_model=HealthResponse)
async def status_check() -> HealthResponse:
    """Return detailed service status."""
    return HealthResponse(status="ok", version="0.1.0")
