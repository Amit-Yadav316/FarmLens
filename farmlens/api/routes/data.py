from __future__ import annotations

from fastapi import APIRouter, Depends

from farmlens.core.dependencies import get_mandi_service, get_weather_service
from farmlens.features.mandi.schemas import PriceResponse
from farmlens.features.mandi.service import MandiService
from farmlens.features.weather.schemas import WeatherResponse
from farmlens.features.weather.service import WeatherService

router = APIRouter()


@router.get("/price", response_model=PriceResponse)
async def get_price(
    crop: str,
    state: str,
    service: MandiService = Depends(get_mandi_service),
) -> PriceResponse:
    """Return latest mandi prices for a crop in a state."""
    return service.get_price(crop, state)


@router.get("/weather", response_model=WeatherResponse)
async def get_weather(
    lat: float,
    lon: float,
    service: WeatherService = Depends(get_weather_service),
) -> WeatherResponse:
    """Return weather forecast and spray advisory for coordinates."""
    return service.get_advisory(lat, lon)
