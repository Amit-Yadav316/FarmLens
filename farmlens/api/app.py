from __future__ import annotations

from fastapi import FastAPI

from farmlens.api.exception_handlers import register_exception_handlers
from farmlens.api.middleware import add_middleware
from farmlens.api.routes import chat, data, health
from farmlens.core.config import get_settings
from farmlens.core.logging import configure_logging


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    get_settings()  # eagerly load and validate settings at startup
    configure_logging()

    app = FastAPI(
        title="FarmLens API",
        description="Multilingual voice-first AI advisory for Indian farmers",
        version="0.1.0",
    )

    add_middleware(app)
    register_exception_handlers(app)

    app.include_router(health.router, tags=["health"])
    app.include_router(data.router, prefix="/api/v1", tags=["data"])
    app.include_router(chat.router, prefix="/api/v1", tags=["chat"])

    return app


app = create_app()
