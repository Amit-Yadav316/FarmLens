from __future__ import annotations

import pytest

from farmlens.features.weather.service import WeatherService


class TestWeatherService:
    """Tests for WeatherService."""

    def test_placeholder(self, settings) -> None:
        """Placeholder — replace with real tests on Day 3."""
        service = WeatherService(settings)
        assert service is not None
