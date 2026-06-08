from __future__ import annotations

from farmlens.core.exceptions import FarmLensException


class WeatherException(FarmLensException):
    """Raised when weather data fetching or spray advisory fails."""
