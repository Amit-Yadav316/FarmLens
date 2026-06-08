from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class Intent(StrEnum):
    """Supported user intents."""

    PRICE = "price"
    WEATHER = "weather"
    DISEASE = "disease"
    SCHEME = "scheme"
    GENERAL = "general"


class IntentResult(BaseModel):
    """Result of intent classification."""

    intent: Intent
    confidence: float
    raw_text: str
