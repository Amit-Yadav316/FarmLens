from __future__ import annotations

import requests
from cachetools import TTLCache

from farmlens.core.config import Settings
from farmlens.features.mandi.constants import CROP_MAP
from farmlens.features.mandi.exceptions import MandiException
from farmlens.features.mandi.schemas import PriceRecord, PriceResponse

_AGMARKNET_URL = "https://api.data.gov.in/resource/{resource_id}"
_REQUEST_TIMEOUT = 30  # Agmarknet (data.gov.in) is slow; allow generous headroom


class MandiService:
    """Fetches live mandi prices from the Agmarknet API."""

    def __init__(self, settings: Settings) -> None:
        self._api_key = settings.data_gov_api_key
        self._resource_id = settings.mandi_resource_id
        self._cache: TTLCache = TTLCache(
            maxsize=100,
            ttl=settings.mandi_cache_ttl,
        )

    def get_price(self, crop: str, state: str) -> PriceResponse:
        """Return latest mandi prices for a crop in the given state."""
        crop_en = self._normalize_crop(crop)
        cache_key = f"{crop_en}:{state}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        raw = self._fetch_from_api(crop_en, state)
        records = [
            PriceRecord(
                market=r["market"],
                crop=r["commodity"],
                variety=r.get("variety", ""),
                min_price=float(r["min_price"]),
                max_price=float(r["max_price"]),
                modal_price=float(r["modal_price"]),
                arrival_date=r["arrival_date"],
            )
            for r in raw
        ]
        result = PriceResponse(crop=crop_en, state=state, records=records)
        self._cache[cache_key] = result
        return result

    def _fetch_from_api(self, crop_en: str, state: str) -> list[dict]:
        """Fetch raw price records from the Agmarknet API."""
        url = _AGMARKNET_URL.format(resource_id=self._resource_id)
        params: dict[str, str | int] = {
            "api-key": self._api_key,
            "format": "json",
            "filters[commodity]": crop_en,
            "filters[state]": state,
            "limit": 10,
        }
        try:
            resp = requests.get(url, params=params, timeout=_REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json().get("records", [])
        except requests.Timeout as e:
            raise MandiException("Agmarknet API timeout") from e
        except requests.HTTPError as e:
            status = e.response.status_code if e.response is not None else "unknown"
            raise MandiException(f"Agmarknet API error: {status}") from e
        except requests.RequestException as e:
            raise MandiException(f"Agmarknet request failed: {e}") from e

    def _normalize_crop(self, crop: str) -> str:
        """Translate a regional-language crop name to its English API name."""
        return CROP_MAP.get(crop, crop)
