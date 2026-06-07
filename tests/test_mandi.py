"""
Day 3 tests -- run after writing price_service.py
Usage: pytest tests/test_mandi.py -v
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestCropMap:
    """Test crop name mapping"""

    def test_hindi_wheat_maps_to_english(self):
        from backend.mandi.price_service import _get_english_name
        assert _get_english_name("गेहूं") == "Wheat"

    def test_hindi_onion_maps_to_english(self):
        from backend.mandi.price_service import _get_english_name
        assert _get_english_name("प्याज") == "Onion"

    def test_english_passthrough(self):
        from backend.mandi.price_service import _get_english_name
        assert _get_english_name("Wheat") == "Wheat"

    def test_unknown_crop_passthrough(self):
        from backend.mandi.price_service import _get_english_name
        result = _get_english_name("xyz_unknown")
        assert result == "xyz_unknown"

    def test_marathi_onion_maps(self):
        from backend.mandi.price_service import _get_english_name
        assert _get_english_name("कांदा") == "Onion"


class TestMandiAPI:
    """Test live API calls -- requires DATA_GOV_API_KEY in .env"""

    def test_wheat_price_returns_data(self):
        from backend.mandi.price_service import get_price
        result = get_price("गेहूं", "Uttar Pradesh", "Agra")
        # API should return data or a proper error message
        assert "response_hi" in result
        assert isinstance(result["response_hi"], str)
        assert len(result["response_hi"]) > 0

    def test_response_contains_rupee_symbol(self):
        from backend.mandi.price_service import get_price
        result = get_price("गेहूं", "Uttar Pradesh")
        if result.get("success"):
            assert "₹" in result["response_hi"]

    def test_unknown_crop_returns_message(self):
        from backend.mandi.price_service import get_price
        result = get_price("xyz_not_a_crop", "Uttar Pradesh")
        assert "response_hi" in result
        # Should return graceful error message
        assert result["success"] == False or "उपलब्ध नहीं" in result.get("response_hi", "")

    def test_caching_works(self):
        from backend.mandi.price_service import get_price, _cache
        _cache.clear()

        # First call
        result1 = get_price("गेहूं", "Uttar Pradesh", "Agra")
        # Second call should hit cache
        result2 = get_price("गेहूं", "Uttar Pradesh", "Agra")

        # Both should return same data
        assert result1["response_hi"] == result2["response_hi"]


class TestResponseFormat:
    """Test response formatting"""

    def test_hindi_response_contains_crop_name(self):
        from backend.mandi.price_service import get_price
        result = get_price("प्याज", "Maharashtra", "Nashik")
        if result.get("success"):
            assert "प्याज" in result["response_hi"]

    def test_response_contains_market_name(self):
        from backend.mandi.price_service import get_price
        result = get_price("गेहूं", "Uttar Pradesh", "Agra")
        if result.get("success"):
            # Should contain मंडी somewhere
            assert "मंडी" in result["response_hi"] or "market" in result["response_hi"].lower()