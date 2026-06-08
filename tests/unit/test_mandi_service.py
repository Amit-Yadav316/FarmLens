from __future__ import annotations

import pytest

from farmlens.features.mandi.service import MandiService


class TestMandiService:
    """Tests for MandiService."""

    def test_placeholder(self, settings) -> None:
        """Placeholder — replace with real tests on Day 2."""
        service = MandiService(settings)
        assert service is not None
