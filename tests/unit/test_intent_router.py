from __future__ import annotations

import pytest

from farmlens.features.intent.router import IntentRouter


class TestIntentRouter:
    """Tests for IntentRouter."""

    def test_placeholder(self, settings) -> None:
        """Placeholder — replace with real tests on Day 5."""
        router = IntentRouter(settings)
        assert router is not None
