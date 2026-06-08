from __future__ import annotations

from pydantic import BaseModel


class WeatherRequest(BaseModel):
    """Request model for weather advisory."""

    lat: float
    lon: float
    crop: str | None = None


class ForecastDay(BaseModel):
    """Weather forecast for a single day."""

    date: str
    temp_min: float
    temp_max: float
    humidity: float
    wind_speed: float
    rain_mm: float
    condition: str


class WeatherResponse(BaseModel):
    """Response model for weather and spray advisory."""

    location: str
    forecast: list[ForecastDay]
    spray_advisory: str
    safe_to_spray: bool
