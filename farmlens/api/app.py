from __future__ import annotations

from fastapi import FastAPI

from farmlens.api.middleware import add_middleware
from farmlens.api.routes import chat, data, health
from farmlens.core.config import get_settings
from farmlens.core.logging import configure_logging


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    configure_logging()

    app = FastAPI(
        title="FarmLens API",
        description="Multilingual voice-first AI advisory for Indian farmers",
        version="0.1.0",
    )

    add_middleware(app)

    app.include_router(health.router, tags=["health"])
    app.include_router(data.router, prefix="/api/v1", tags=["data"])
    app.include_router(chat.router, prefix="/api/v1", tags=["chat"])

    return app


app = create_app()
