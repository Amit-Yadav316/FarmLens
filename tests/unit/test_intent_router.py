from __future__ import annotations

from farmlens.features.intent.router import IntentRouter
from farmlens.features.intent.schemas import Intent


class TestIntentRouter:
    """Tests for IntentRouter keyword classification."""

    def test_price_intent_hindi(self, settings) -> None:
        """A Hindi price question is classified as PRICE."""
        router = IntentRouter(settings)
        result = router.classify("गेहूं का भाव क्या है मंडी में")
        assert result.intent == Intent.PRICE

    def test_price_intent_english(self, settings) -> None:
        """An English price question is classified as PRICE."""
        router = IntentRouter(settings)
        result = router.classify("what is the market rate of wheat")
        assert result.intent == Intent.PRICE

    def test_weather_intent_hindi(self, settings) -> None:
        """A Hindi weather question is classified as WEATHER."""
        router = IntentRouter(settings)
        result = router.classify("कल मौसम कैसा रहेगा बारिश होगी")
        assert result.intent == Intent.WEATHER

    def test_disease_intent_hindi(self, settings) -> None:
        """A Hindi disease question is classified as DISEASE."""
        router = IntentRouter(settings)
        result = router.classify("मेरी फसल में रोग और कीट लग गए हैं")
        assert result.intent == Intent.DISEASE

    def test_scheme_intent_hindi(self, settings) -> None:
        """A Hindi scheme question is classified as SCHEME."""
        router = IntentRouter(settings)
        result = router.classify("किसान योजना और सब्सिडी की जानकारी दो")
        assert result.intent == Intent.SCHEME

    def test_general_intent_when_no_keywords(self, settings) -> None:
        """Text with no known keywords falls back to GENERAL."""
        router = IntentRouter(settings)
        result = router.classify("नमस्ते आप कैसे हैं")
        assert result.intent == Intent.GENERAL

    def test_result_preserves_raw_text(self, settings) -> None:
        """The original text is preserved in the result."""
        router = IntentRouter(settings)
        text = "गेहूं का भाव"
        result = router.classify(text)
        assert result.raw_text == text

    def test_highest_scoring_intent_wins(self, settings) -> None:
        """When multiple intents match, the one with more keywords wins."""
        router = IntentRouter(settings)
        # two weather keywords (मौसम, बारिश) vs one price keyword (भाव)
        result = router.classify("मौसम और बारिश का भाव")
        assert result.intent == Intent.WEATHER

    def test_classify_is_case_insensitive(self, settings) -> None:
        """English keyword matching ignores case."""
        router = IntentRouter(settings)
        result = router.classify("WHAT IS THE PRICE OF WHEAT")
        assert result.intent == Intent.PRICE
