from __future__ import annotations

import requests
from cachetools import TTLCache

from farmlens.core.config import Settings
from farmlens.features.weather.constants import (
    SPRAY_HUMIDITY_LIMIT_PCT,
    SPRAY_RAIN_LIMIT_MM,
    SPRAY_WIND_LIMIT_KMH,
)
from farmlens.features.weather.exceptions import WeatherException
from farmlens.features.weather.schemas import ForecastDay, WeatherResponse

_OWM_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


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
        cache_key = f"{lat:.4f}:{lon:.4f}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        raw = self._fetch_forecast(lat, lon)
        result = self._apply_rules(raw)
        self._cache[cache_key] = result
        return result

    def _fetch_forecast(self, lat: float, lon: float) -> dict:
        """Fetch raw 5-day forecast from OpenWeatherMap."""
        params: dict[str, str | float | int] = {
            "lat": lat,
            "lon": lon,
            "appid": self._api_key,
            "units": "metric",
            "cnt": 40,
        }
        try:
            resp = requests.get(_OWM_FORECAST_URL, params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.Timeout as e:
            raise WeatherException("OpenWeatherMap API timeout") from e
        except requests.HTTPError as e:
            status = e.response.status_code if e.response is not None else "unknown"
            raise WeatherException(f"OpenWeatherMap API error: {status}") from e
        except requests.RequestException as e:
            raise WeatherException(f"OpenWeatherMap request failed: {e}") from e

    def _apply_rules(self, raw: dict) -> WeatherResponse:
        """Apply spray safety rules to the raw forecast data."""
        city = raw.get("city", {}).get("name", "Unknown")
        forecast = self._parse_days(raw.get("list", []))
        safe, advisory = self._spray_decision(forecast)
        return WeatherResponse(
            location=city,
            forecast=forecast,
            spray_advisory=advisory,
            safe_to_spray=safe,
        )

    def _parse_days(self, items: list[dict]) -> list[ForecastDay]:
        """Group 3-hourly slots by date and aggregate into daily forecasts."""
        days: dict[str, list] = {}
        for item in items:
            days.setdefault(item["dt_txt"][:10], []).append(item)
        return [self._aggregate_day(date, slots) for date, slots in list(days.items())[:5]]

    def _aggregate_day(self, date: str, slots: list[dict]) -> ForecastDay:
        """Aggregate 3-hourly slots into a single ForecastDay."""
        temps = [s["main"]["temp"] for s in slots]
        humids = [s["main"]["humidity"] for s in slots]
        winds = [s["wind"]["speed"] * 3.6 for s in slots]  # m/s → km/h
        rains = [s.get("rain", {}).get("3h", 0.0) for s in slots]
        mid = slots[len(slots) // 2]
        return ForecastDay(
            date=date,
            temp_min=min(temps),
            temp_max=max(temps),
            humidity=max(humids),
            wind_speed=max(winds),
            rain_mm=sum(rains),
            condition=mid["weather"][0]["description"],
        )

    def _spray_decision(self, forecast: list[ForecastDay]) -> tuple[bool, str]:
        """Return (safe_to_spray, advisory_message) based on today's forecast."""
        if not forecast:
            return False, "Weather data unavailable — do not spray"
        today = forecast[0]
        if today.wind_speed > SPRAY_WIND_LIMIT_KMH:
            return False, f"Wind too high ({today.wind_speed:.1f} km/h) — do not spray"
        if today.rain_mm > SPRAY_RAIN_LIMIT_MM:
            return False, f"Rain expected ({today.rain_mm:.1f} mm) — do not spray"
        if today.humidity > SPRAY_HUMIDITY_LIMIT_PCT:
            return False, f"Humidity too high ({today.humidity:.0f}%) — do not spray"
        return True, "Conditions are safe for spraying today"
