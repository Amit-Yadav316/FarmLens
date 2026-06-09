from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from farmlens.features.weather.exceptions import WeatherException
from farmlens.features.weather.service import WeatherService

# wind 2 m/s = 7.2 km/h, humidity 65%, rain 0.5mm — all safe
_SAFE_SLOT = {
    "dt_txt": "2026-06-09 12:00:00",
    "main": {"temp": 32.0, "temp_min": 28.0, "temp_max": 36.0, "humidity": 65},
    "wind": {"speed": 2.0},
    "weather": [{"description": "clear sky"}],
    "rain": {"3h": 0.5},
}

# wind 5 m/s = 18 km/h — exceeds 15 km/h limit
_HIGH_WIND_SLOT = {**_SAFE_SLOT, "wind": {"speed": 5.0}}

# rain 2mm per slot × 3 slots = 6mm total — exceeds 5mm limit
_HEAVY_RAIN_SLOT = {**_SAFE_SLOT, "rain": {"3h": 2.5}}

# humidity 95% — exceeds 90% limit
_HIGH_HUMIDITY_SLOT = {**_SAFE_SLOT, "main": {**_SAFE_SLOT["main"], "humidity": 95}}


def _owm_response(slot: dict) -> dict:
    return {"city": {"name": "Lucknow"}, "list": [slot, slot, slot]}


@pytest.fixture
def mock_api():
    """Mock requests.get for WeatherService with safe conditions."""
    with patch("farmlens.features.weather.service.requests.get") as mock_get:
        mock_get.return_value.json.return_value = _owm_response(_SAFE_SLOT)
        mock_get.return_value.raise_for_status = MagicMock()
        yield mock_get


class TestWeatherService:
    """Tests for WeatherService."""

    def test_get_advisory_returns_response(self, settings, mock_api) -> None:
        """get_advisory returns a WeatherResponse with forecast and advisory."""
        service = WeatherService(settings)
        result = service.get_advisory(26.8467, 80.9462)
        assert result.location == "Lucknow"
        assert len(result.forecast) == 1
        assert result.forecast[0].condition == "clear sky"

    def test_safe_to_spray_when_conditions_good(self, settings, mock_api) -> None:
        """Returns safe_to_spray=True when wind, rain, and humidity are within limits."""
        service = WeatherService(settings)
        result = service.get_advisory(26.8467, 80.9462)
        assert result.safe_to_spray is True
        assert "safe" in result.spray_advisory.lower()

    def test_unsafe_when_wind_too_high(self, settings) -> None:
        """Returns safe_to_spray=False when wind exceeds 15 km/h."""
        service = WeatherService(settings)
        with patch("farmlens.features.weather.service.requests.get") as mock_get:
            mock_get.return_value.json.return_value = _owm_response(_HIGH_WIND_SLOT)
            mock_get.return_value.raise_for_status = MagicMock()
            result = service.get_advisory(26.8467, 80.9462)
        assert result.safe_to_spray is False
        assert "Wind" in result.spray_advisory

    def test_unsafe_when_heavy_rain(self, settings) -> None:
        """Returns safe_to_spray=False when total rain exceeds 5 mm."""
        service = WeatherService(settings)
        with patch("farmlens.features.weather.service.requests.get") as mock_get:
            mock_get.return_value.json.return_value = _owm_response(_HEAVY_RAIN_SLOT)
            mock_get.return_value.raise_for_status = MagicMock()
            result = service.get_advisory(26.8467, 80.9462)
        assert result.safe_to_spray is False
        assert "Rain" in result.spray_advisory

    def test_unsafe_when_humidity_too_high(self, settings) -> None:
        """Returns safe_to_spray=False when humidity exceeds 90%."""
        service = WeatherService(settings)
        with patch("farmlens.features.weather.service.requests.get") as mock_get:
            mock_get.return_value.json.return_value = _owm_response(_HIGH_HUMIDITY_SLOT)
            mock_get.return_value.raise_for_status = MagicMock()
            result = service.get_advisory(26.8467, 80.9462)
        assert result.safe_to_spray is False
        assert "Humidity" in result.spray_advisory

    def test_cache_hit_on_second_call(self, settings, mock_api) -> None:
        """Second call with same coordinates hits cache, not the API."""
        service = WeatherService(settings)
        service.get_advisory(26.8467, 80.9462)
        service.get_advisory(26.8467, 80.9462)
        assert mock_api.call_count == 1

    def test_timeout_raises_weather_exception(self, settings) -> None:
        """API timeout raises WeatherException."""
        service = WeatherService(settings)
        with patch("farmlens.features.weather.service.requests.get") as mock_get:
            mock_get.side_effect = requests.Timeout
            with pytest.raises(WeatherException, match="timeout"):
                service.get_advisory(26.8467, 80.9462)

    def test_http_error_raises_weather_exception(self, settings) -> None:
        """Non-200 response raises WeatherException."""
        service = WeatherService(settings)
        with patch("farmlens.features.weather.service.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 401
            mock_get.side_effect = requests.HTTPError(response=mock_resp)
            with pytest.raises(WeatherException):
                service.get_advisory(26.8467, 80.9462)

    def test_empty_forecast_list_is_unsafe(self, settings) -> None:
        """Empty forecast data from API returns safe_to_spray=False."""
        service = WeatherService(settings)
        with patch("farmlens.features.weather.service.requests.get") as mock_get:
            mock_get.return_value.json.return_value = {"city": {"name": "X"}, "list": []}
            mock_get.return_value.raise_for_status = MagicMock()
            result = service.get_advisory(0.0, 0.0)
        assert result.safe_to_spray is False
