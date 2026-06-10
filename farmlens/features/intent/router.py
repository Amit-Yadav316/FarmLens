from __future__ import annotations

from farmlens.core.config import Settings
from farmlens.features.intent.constants import (
    DISEASE_KEYWORDS,
    PRICE_KEYWORDS,
    SCHEME_KEYWORDS,
    WEATHER_KEYWORDS,
)
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
        scores: dict[Intent, int] = {
            Intent.PRICE: self._count_matches(text, PRICE_KEYWORDS),
            Intent.WEATHER: self._count_matches(text, WEATHER_KEYWORDS),
            Intent.DISEASE: self._count_matches(text, DISEASE_KEYWORDS),
            Intent.SCHEME: self._count_matches(text, SCHEME_KEYWORDS),
        }
        best_intent = max(scores, key=lambda intent: scores[intent])
        if scores[best_intent] == 0:
            return Intent.GENERAL
        return best_intent

    @staticmethod
    def _count_matches(text: str, keywords: list[str]) -> int:
        """Count how many keywords appear in the text."""
        return sum(1 for keyword in keywords if keyword.lower() in text)
