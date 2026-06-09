from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from farmlens.features.mandi.exceptions import MandiException
from farmlens.features.mandi.service import MandiService

_MOCK_RECORDS = [
    {
        "market": "Lucknow",
        "commodity": "Wheat",
        "variety": "Other",
        "min_price": "2100",
        "max_price": "2300",
        "modal_price": "2200",
        "arrival_date": "07/06/2026",
    }
]


@pytest.fixture
def mock_api():
    """Mock requests.get for MandiService with one wheat record."""
    with patch("farmlens.features.mandi.service.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"records": _MOCK_RECORDS}
        mock_get.return_value.raise_for_status = MagicMock()
        yield mock_get


class TestMandiService:
    """Tests for MandiService."""

    def test_get_price_returns_response(self, settings, mock_api) -> None:
        """get_price returns a PriceResponse with correct fields."""
        service = MandiService(settings)
        result = service.get_price("Wheat", "Uttar Pradesh")
        assert result.crop == "Wheat"
        assert result.state == "Uttar Pradesh"
        assert result.source == "Agmarknet"
        assert len(result.records) == 1
        assert result.records[0].modal_price == 2200.0
        assert result.records[0].market == "Lucknow"

    def test_get_price_normalizes_hindi_crop(self, settings, mock_api) -> None:
        """Hindi crop name is translated to English in the response."""
        service = MandiService(settings)
        result = service.get_price("गेहूं", "Punjab")
        assert result.crop == "Wheat"

    def test_get_price_normalizes_punjabi_crop(self, settings, mock_api) -> None:
        """Punjabi crop name is translated to English in the response."""
        service = MandiService(settings)
        result = service.get_price("ਕਣਕ", "Punjab")
        assert result.crop == "Wheat"

    def test_get_price_uses_cache_on_second_call(self, settings, mock_api) -> None:
        """Second identical call hits cache and does not call the API again."""
        service = MandiService(settings)
        service.get_price("Wheat", "Punjab")
        service.get_price("Wheat", "Punjab")
        assert mock_api.call_count == 1

    def test_different_states_are_cached_separately(self, settings, mock_api) -> None:
        """Different state queries each hit the API once."""
        service = MandiService(settings)
        service.get_price("Wheat", "Punjab")
        service.get_price("Wheat", "Haryana")
        assert mock_api.call_count == 2

    def test_normalize_crop_unknown_passthrough(self, settings) -> None:
        """Unknown crop name is passed through unchanged."""
        service = MandiService(settings)
        assert service._normalize_crop("Bajra") == "Bajra"

    def test_normalize_crop_hindi(self, settings) -> None:
        """Hindi crop names map to their English equivalents."""
        service = MandiService(settings)
        assert service._normalize_crop("सरसों") == "Mustard"
        assert service._normalize_crop("मक्का") == "Maize"
        assert service._normalize_crop("आलू") == "Potato"

    def test_timeout_raises_mandi_exception(self, settings) -> None:
        """API timeout raises MandiException with 'timeout' in the message."""
        service = MandiService(settings)
        with patch("farmlens.features.mandi.service.requests.get") as mock_get:
            mock_get.side_effect = requests.Timeout
            with pytest.raises(MandiException, match="timeout"):
                service.get_price("Wheat", "Punjab")

    def test_http_error_raises_mandi_exception(self, settings) -> None:
        """Non-200 HTTP response raises MandiException."""
        service = MandiService(settings)
        with patch("farmlens.features.mandi.service.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 403
            mock_get.side_effect = requests.HTTPError(response=mock_resp)
            with pytest.raises(MandiException):
                service.get_price("Wheat", "Punjab")

    def test_empty_records_returns_empty_list(self, settings) -> None:
        """API returning no records gives a PriceResponse with empty records."""
        service = MandiService(settings)
        with patch("farmlens.features.mandi.service.requests.get") as mock_get:
            mock_get.return_value.json.return_value = {"records": []}
            mock_get.return_value.raise_for_status = MagicMock()
            result = service.get_price("Wheat", "Punjab")
        assert result.records == []
