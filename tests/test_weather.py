"""
Day 4 tests -- run after writing advisory.py
Usage: pytest tests/test_weather.py -v
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Delhi coordinates for testing
DELHI_LAT = 28.6139
DELHI_LON = 77.2090


class TestLocationMap:
    """Test city to coordinates mapping"""

    def test_hindi_city_agra(self):
        from backend.weather.advisory import get_coordinates
        result = get_coordinates("आगरा")
        assert result is not None
        lat, lon = result
        assert 26 < lat < 28
        assert 77 < lon < 79

    def test_english_city_delhi(self):
        from backend.weather.advisory import get_coordinates
        result = get_coordinates("Delhi")
        assert result is not None

    def test_unknown_city_returns_none(self):
        from backend.weather.advisory import get_coordinates
        result = get_coordinates("xyz_unknown_city")
        assert result is None

    def test_hindi_pune(self):
        from backend.weather.advisory import get_coordinates
        result = get_coordinates("पुणे")
        assert result is not None
        lat, lon = result
        assert 17 < lat < 20
        assert 72 < lon < 75


class TestSprayAdvisory:
    """Test spray advisory logic -- requires OPENWEATHER_API_KEY in .env"""

    def test_returns_spray_ok_boolean(self):
        from backend.weather.advisory import spray_advisory
        result = spray_advisory(DELHI_LAT, DELHI_LON)
        assert "spray_ok" in result
        assert isinstance(result["spray_ok"], bool) or result["spray_ok"] is None

    def test_returns_hindi_response(self):
        from backend.weather.advisory import spray_advisory
        result = spray_advisory(DELHI_LAT, DELHI_LON)
        assert "response_hi" in result
        assert len(result["response_hi"]) > 0

    def test_response_contains_decision(self):
        from backend.weather.advisory import spray_advisory
        result = spray_advisory(DELHI_LAT, DELHI_LON)
        if result.get("success"):
            # Must contain yes or no decision
            has_yes = "✅" in result["response_hi"]
            has_no  = "❌" in result["response_hi"]
            assert has_yes or has_no

    def test_caching_works(self):
        from backend.weather.advisory import spray_advisory, _cache
        _cache.clear()

        result1 = spray_advisory(DELHI_LAT, DELHI_LON)
        result2 = spray_advisory(DELHI_LAT, DELHI_LON)

        # Second call should return cached result
        assert result1["response_hi"] == result2["response_hi"]

    def test_weather_data_present(self):
        from backend.weather.advisory import spray_advisory
        result = spray_advisory(DELHI_LAT, DELHI_LON)
        if result.get("success"):
            assert "temp" in result
            assert "humidity" in result
            assert "wind_kmh" in result
            assert "rain_prob" in result


class TestSprayRules:
    """Test the spray rules logic directly without API"""

    def test_high_rain_means_no_spray(self):
        """Simulate high rain probability"""
        from backend.weather.advisory import SPRAY_RULES
        rain_prob = 0.80   # 80% rain
        assert rain_prob > SPRAY_RULES["rain_prob_max"]

    def test_high_wind_means_no_spray(self):
        from backend.weather.advisory import SPRAY_RULES
        wind_speed = 20.0  # 20 km/h
        assert wind_speed > SPRAY_RULES["wind_speed_max"]

    def test_normal_conditions_allow_spray(self):
        from backend.weather.advisory import SPRAY_RULES
        rain_prob = 0.10   # 10%
        wind_kmh  = 8.0    # 8 km/h
        humidity  = 60     # 60%
        temp      = 25     # 25°C

        assert rain_prob  <= SPRAY_RULES["rain_prob_max"]
        assert wind_kmh   <= SPRAY_RULES["wind_speed_max"]
        assert humidity   <= SPRAY_RULES["humidity_max"]
        assert temp       >= SPRAY_RULES["temp_min"]
        assert temp       <= SPRAY_RULES["temp_max"]