from __future__ import annotations

from cachetools import TTLCache

from farmlens.core.config import Settings
from farmlens.features.weather.exceptions import WeatherException
from farmlens.features.weather.schemas import WeatherResponse


class WeatherService:
    """Fetches weather forecasts and generates spray advisories."""

    def __init__(self, settings: Settings) -> None:
        self._api_key = settings.openweather_api_key
        self._cache: TTLCache = TTLCache(
            maxsize=50,
            ttl=settings.weather_cache_ttl,
        )

    def get_advisory(self, lat: float, lon: float) -> WeatherResponse:
        """Return weather forecast and spray advisory for coordinates."""
        raise NotImplementedError

    def _fetch_forecast(self, lat: float, lon: float) -> dict:
        """Fetch raw 5-day forecast from OpenWeatherMap."""
        raise NotImplementedError

    def _apply_rules(self, forecast: dict) -> WeatherResponse:
        """Apply spray safety rules to the raw forecast data."""
        raise NotImplementedError
