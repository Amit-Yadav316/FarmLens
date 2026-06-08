from __future__ import annotations

import pytest

from farmlens.core.config import Settings


@pytest.fixture
def settings() -> Settings:
    """Return a test Settings instance with dummy API keys."""
    return Settings(
        data_gov_api_key="test-key",
        openweather_api_key="test-key",
        hf_token="test-token",
        mandi_cache_ttl=60,
        weather_cache_ttl=60,
    )
