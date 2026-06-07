import requests
import json
from pathlib import Path
from cachetools import TTLCache
from backend.config.settings import get_settings

settings = get_settings()

# ── Cache -- weather changes every 30 min ─────────────────
_cache = TTLCache(maxsize=50, ttl=settings.weather_cache_ttl)

# ── Load location map ──────────────────────────────────────
_LOCATION_MAP_PATH = Path("data/location_map.json")

def _load_location_map() -> dict:
    with open(_LOCATION_MAP_PATH, encoding="utf-8") as f:
        return json.load(f)

def get_coordinates(city: str) -> tuple[float, float] | None:
    """
    Convert city name (Hindi or English) to lat/lon.
    Returns (lat, lon) or None if not found.
    """
    loc_map = _load_location_map()
    if city in loc_map:
        entry = loc_map[city]
        return entry["lat"], entry["lon"]
    return None


# ── Spray rules -- based on agronomist guidelines ─────────
# These are the actual rules used by agricultural extension officers

SPRAY_RULES = {
    "rain_prob_max":   0.40,   # >40% rain chance → don't spray
    "wind_speed_max":  15.0,   # >15 km/h wind → don't spray
    "humidity_max":    85,     # >85% humidity → don't spray
    "temp_min":        10.0,   # <10°C too cold for most pesticides
    "temp_max":        40.0,   # >40°C pesticide evaporates too fast
}


# ── Main advisory function ────────────────────────────────

def spray_advisory(
    lat: float,
    lon: float,
    lang: str = "hi"
) -> dict:
    """
    Check if weather conditions are suitable for pesticide spraying.

    Uses OpenWeatherMap free API (2.5/forecast endpoint).
    Checks next 8 hours (4 forecast points x 3hr intervals).

    Args:
        lat:  Latitude of farm
        lon:  Longitude of farm
        lang: Response language code

    Returns:
        dict with spray_ok (bool), reasons, weather data, response_hi
    """
    cache_key = f"{lat:.2f}_{lon:.2f}"
    if cache_key in _cache:
        return _cache[cache_key]

    try:
        forecast = _fetch_forecast(lat, lon)
    except Exception as e:
        return _error_response(f"मौसम जानकारी लाने में समस्या: {str(e)}")

    # Analyse next 8 hours (first 3 forecast points)
    next_hours = forecast[:3]

    # Extract worst-case values across all forecast points
    max_rain_prob  = max(h.get("pop", 0) for h in next_hours)
    max_wind_kmh   = max(
        h.get("wind", {}).get("speed", 0) * 3.6   # m/s to km/h
        for h in next_hours
    )
    current_humidity = next_hours[0].get("main", {}).get("humidity", 0)
    current_temp     = next_hours[0].get("main", {}).get("temp", 25)

    # Apply rules
    reasons_no  = []   # reasons NOT to spray
    reasons_yes = []   # favourable conditions

    if max_rain_prob > SPRAY_RULES["rain_prob_max"]:
        reasons_no.append(f"बारिश की {int(max_rain_prob * 100)}% संभावना है")

    if max_wind_kmh > SPRAY_RULES["wind_speed_max"]:
        reasons_no.append(f"तेज़ हवा चल रही है ({max_wind_kmh:.0f} km/h)")

    if current_humidity > SPRAY_RULES["humidity_max"]:
        reasons_no.append(f"नमी बहुत अधिक है ({current_humidity}%)")

    if current_temp < SPRAY_RULES["temp_min"]:
        reasons_no.append(f"तापमान बहुत कम है ({current_temp:.0f}°C)")

    if current_temp > SPRAY_RULES["temp_max"]:
        reasons_no.append(f"तापमान बहुत अधिक है ({current_temp:.0f}°C)")

    if not reasons_no:
        reasons_yes.append("मौसम साफ है")
        reasons_yes.append(f"नमी सामान्य है ({current_humidity}%)")
        reasons_yes.append(f"हवा की गति ठीक है ({max_wind_kmh:.0f} km/h)")

    spray_ok = len(reasons_no) == 0

    # Format response
    response_hi = _format_response(
        spray_ok, reasons_no, reasons_yes,
        current_temp, current_humidity,
        max_wind_kmh, max_rain_prob
    )

    result = {
        "spray_ok":    spray_ok,
        "reasons_no":  reasons_no,
        "reasons_yes": reasons_yes,
        "temp":        round(current_temp, 1),
        "humidity":    current_humidity,
        "wind_kmh":    round(max_wind_kmh, 1),
        "rain_prob":   int(max_rain_prob * 100),
        "response_hi": response_hi,
        "success":     True,
    }

    _cache[cache_key] = result
    return result


def _fetch_forecast(lat: float, lon: float) -> list:
    """Fetch 5-day / 3-hour forecast from OpenWeatherMap free API"""
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat":   lat,
        "lon":   lon,
        "appid": settings.openweather_api_key,
        "units": "metric",   # Celsius, m/s
        "cnt":   4,          # next 4 x 3hr = 12 hours
    }
    response = requests.get(url, params=params, timeout=8)
    response.raise_for_status()
    data = response.json()
    return data.get("list", [])


def _format_response(
    spray_ok: bool,
    reasons_no: list,
    reasons_yes: list,
    temp: float,
    humidity: int,
    wind: float,
    rain_prob: float
) -> str:
    """Format a clear Hindi advisory message"""

    if spray_ok:
        response = "✅ आज छिड़काव कर सकते हैं\n\n"
        response += "अनुकूल परिस्थितियां:\n"
        for r in reasons_yes:
            response += f"• {r}\n"
        response += f"\nमौसम: {temp:.0f}°C | नमी: {humidity}% | हवा: {wind:.0f} km/h"
        response += "\n\nसुझाव: सुबह जल्दी (8-10 बजे) या शाम को (5-7 बजे) छिड़काव करें।"
    else:
        response = "❌ आज छिड़काव न करें\n\n"
        response += "कारण:\n"
        for r in reasons_no:
            response += f"• {r}\n"
        response += f"\nमौसम: {temp:.0f}°C | नमी: {humidity}% | हवा: {wind:.0f} km/h"
        response += "\n\nकल फिर जांचें।"

    return response


def _error_response(message: str) -> dict:
    return {
        "spray_ok":    None,
        "success":     False,
        "response_hi": message,
    }


# ── 3-day forecast summary ────────────────────────────────

def get_forecast_summary(lat: float, lon: float) -> dict:
    """
    Get a 3-day weather summary for irrigation planning.
    Answers: "अगले 3 दिन बारिश आएगी?"
    """
    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "lat":   lat,
            "lon":   lon,
            "appid": settings.openweather_api_key,
            "units": "metric",
            "cnt":   24,   # 3 days x 8 points
        }
        response = requests.get(url, params=params, timeout=8)
        data = response.json()
        forecasts = data.get("list", [])

        # Group by day
        days = {}
        for f in forecasts:
            date = f["dt_txt"].split(" ")[0]
            if date not in days:
                days[date] = []
            days[date].append(f)

        summary = "अगले 3 दिनों का मौसम:\n\n"
        for i, (date, points) in enumerate(list(days.items())[:3]):
            max_rain = max(p.get("pop", 0) for p in points)
            avg_temp = sum(p["main"]["temp"] for p in points) / len(points)
            rain_text = (
                "बारिश की संभावना" if max_rain > 0.4
                else "बारिश की संभावना कम"
            )
            summary += f"दिन {i+1} ({date}): {avg_temp:.0f}°C | {rain_text} ({int(max_rain*100)}%)\n"

        return {"response_hi": summary, "success": True}

    except Exception as e:
        return {"response_hi": "मौसम जानकारी उपलब्ध नहीं है।", "success": False}