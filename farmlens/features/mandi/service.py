from __future__ import annotations

from cachetools import TTLCache

from farmlens.core.config import Settings
from farmlens.features.mandi.exceptions import MandiException
from farmlens.features.mandi.schemas import PriceResponse


class MandiService:
    """Fetches live mandi prices from the Agmarknet API."""

    def __init__(self, settings: Settings) -> None:
        self._api_key = settings.data_gov_api_key
        self._cache: TTLCache = TTLCache(
            maxsize=100,
            ttl=settings.mandi_cache_ttl,
        )

    def get_price(self, crop: str, state: str) -> PriceResponse:
        """Return latest mandi prices for a crop in the given state."""
        raise NotImplementedError

    def _fetch_from_api(self, crop_en: str, state: str) -> dict:
        """Fetch raw price data from the Agmarknet API."""
        raise NotImplementedError

    def _normalize_crop(self, crop: str) -> str:
        """Translate a regional crop name to its English API name."""
        raise NotImplementedError
