from __future__ import annotations

import pytest

from farmlens.features.rag.pipeline import RAGPipeline


class TestRAGPipeline:
    """Tests for RAGPipeline."""

    def test_placeholder(self, settings) -> None:
        """Placeholder — replace with real tests on Day 4."""
        pipeline = RAGPipeline(settings)
        assert pipeline is not None

    def test_is_ready_before_init(self, settings) -> None:
        """Pipeline should not be ready before initialize() is called."""
        pipeline = RAGPipeline(settings)
        assert pipeline.is_ready is False
