from __future__ import annotations

from farmlens.core.config import Settings
from farmlens.features.intent.constants import (
    DISEASE_KEYWORDS,
    PRICE_KEYWORDS,
    SCHEME_KEYWORDS,
    WEATHER_KEYWORDS,
)
from farmlens.features.intent.exceptions import IntentException
from farmlens.features.intent.schemas import Intent, IntentResult


class IntentRouter:
    """Routes user queries to the correct feature handler via keyword matching."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def classify(self, text: str) -> IntentResult:
        """Classify user text into an Intent."""
        lowered = text.lower()
        match self._detect_intent(lowered):
            case Intent.PRICE:
                return IntentResult(intent=Intent.PRICE, confidence=1.0, raw_text=text)
            case Intent.WEATHER:
                return IntentResult(intent=Intent.WEATHER, confidence=1.0, raw_text=text)
            case Intent.DISEASE:
                return IntentResult(intent=Intent.DISEASE, confidence=1.0, raw_text=text)
            case Intent.SCHEME:
                return IntentResult(intent=Intent.SCHEME, confidence=1.0, raw_text=text)
            case _:
                return IntentResult(intent=Intent.GENERAL, confidence=1.0, raw_text=text)

    def _detect_intent(self, text: str) -> Intent:
        """Return the best-matching intent for the lowercased text."""
        raise NotImplementedError
