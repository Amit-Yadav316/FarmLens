import requests
import json
from pathlib import Path
from cachetools import TTLCache
from backend.config.settings import get_settings

settings = get_settings()

# ── Cache -- prices don't change every minute ──────────────
# TTLCache: max 100 entries, each lives for 1 hour
_cache = TTLCache(maxsize=100, ttl=settings.mandi_cache_ttl)

# ── Load crop map from JSON ────────────────────────────────
_CROP_MAP_PATH = Path("data/crop_map.json")

def _load_crop_map() -> dict:
    with open(_CROP_MAP_PATH, encoding="utf-8") as f:
        return json.load(f)

def _get_english_name(crop_input: str) -> str:
    """
    Convert Hindi/Marathi/Punjabi/Telugu crop name to English.
    Falls back to input if not found.
    """
    crop_map = _load_crop_map()

    # Only check forward maps -- Indian language to English
    # Do NOT check english_to_hindi (would convert Wheat -> गेहूं)
    forward_maps = [
        "hindi_to_english",
        "marathi_to_english",
        "punjabi_to_english",
        "telugu_to_english",
    ]

    for map_key in forward_maps:
        lang_map = crop_map.get(map_key, {})
        for k, v in lang_map.items():
            if k.lower() == crop_input.lower():
                return v

    # Not found in any map -- return as-is
    # Handles English input like "Wheat" correctly
    return crop_input


# ── Main price fetch function ──────────────────────────────

def get_price(
    crop: str,
    state: str,
    district: str = None,
    lang: str = "hi"
) -> dict:
    """
    Fetch live mandi price from Agmarknet via data.gov.in API.

    Args:
        crop:     Crop name in any Indian language or English
        state:    State name in English e.g. "Uttar Pradesh"
        district: Optional district name e.g. "Agra"
        lang:     Response language code (hi, mr, pa, te, bn)

    Returns:
        dict with keys: crop, market, state, min_price,
                        max_price, modal_price, date, response_hi
    """
    # Convert to English for API
    crop_en = _get_english_name(crop)

    # Cache key
    cache_key = f"{crop_en}_{state}_{district}"
    if cache_key in _cache:
        return _cache[cache_key]

    # Build API params
    params = {
        "api-key":          settings.data_gov_api_key,
        "format":           "json",
        "filters[State]":   state,
        "filters[Commodity]": crop_en,
        "limit":            "5",
    }
    if district:
        params["filters[District]"] = district

    url = f"https://api.data.gov.in/resource/{settings.mandi_resource_id}"

    try:
        response = requests.get(url, params=params, timeout=8)
        response.raise_for_status()
        data = response.json()

    except requests.exceptions.Timeout:
        return _error_response(crop, "सर्वर से जवाब आने में देरी हो रही है। थोड़ी देर बाद कोशिश करें।")

    except requests.exceptions.RequestException as e:
        return _error_response(crop, f"इंटरनेट कनेक्शन की समस्या है।")

    records = data.get("records", [])

    if not records:
        return _error_response(
            crop,
            f"माफ करना, {crop} का भाव अभी {state} में उपलब्ध नहीं है। "
            f"कृपया बाद में कोशिश करें।"
        )

    # Use first record
    rec = records[0]

    result = {
        "crop":        crop,
        "crop_en":     crop_en,
        "market":      rec.get("Market", ""),
        "state":       rec.get("State", state),
        "district":    rec.get("District", ""),
        "min_price":   rec.get("Min Price", "N/A"),
        "max_price":   rec.get("Max Price", "N/A"),
        "modal_price": rec.get("Modal Price", "N/A"),
        "date":        rec.get("Arrival Date", "आज"),
        "response_hi": _format_hindi_response(crop, rec),
        "success":     True,
    }

    # Cache successful result
    _cache[cache_key] = result
    return result


def _format_hindi_response(crop: str, rec: dict) -> str:
    """Format a natural Hindi response from API record"""
    market  = rec.get("Market", "")
    state   = rec.get("State", "")
    min_p   = rec.get("Min Price", "N/A")
    max_p   = rec.get("Max Price", "N/A")
    modal_p = rec.get("Modal Price", "N/A")
    date    = rec.get("Arrival Date", "आज")

    return (
        f"{market} मंडी में {crop} का भाव ({date}):\n"
        f"न्यूनतम: ₹{min_p} प्रति क्विंटल\n"
        f"अधिकतम: ₹{max_p} प्रति क्विंटल\n"
        f"सामान्य: ₹{modal_p} प्रति क्विंटल"
    )


def _error_response(crop: str, message: str) -> dict:
    return {
        "crop":        crop,
        "success":     False,
        "response_hi": message,
    }


# ── Get multiple markets for comparison ───────────────────

def get_best_market(crop: str, state: str) -> dict:
    """
    Fetch top 5 markets and return the one with highest modal price.
    Helps farmer decide where to sell for best price.
    """
    crop_en = _get_english_name(crop)

    params = {
        "api-key":            settings.data_gov_api_key,
        "format":             "json",
        "filters[State]":     state,
        "filters[Commodity]": crop_en,
        "limit":              "10",
    }

    url = f"https://api.data.gov.in/resource/{settings.mandi_resource_id}"

    try:
        response = requests.get(url, params=params, timeout=8)
        data = response.json()
        records = data.get("records", [])

        if not records:
            return _error_response(crop, f"{crop} का भाव उपलब्ध नहीं है।")

        # Sort by modal price descending
        records.sort(
            key=lambda x: float(x.get("Modal Price", 0) or 0),
            reverse=True
        )

        best = records[0]
        response_hi = (
            f"{state} में सबसे अच्छा भाव:\n"
            f"मंडी: {best.get('Market')}\n"
            f"सामान्य भाव: ₹{best.get('Modal Price')} प्रति क्विंटल\n\n"
            f"अन्य मंडियां:\n"
        )
        for rec in records[1:4]:
            response_hi += (
                f"- {rec.get('Market')}: ₹{rec.get('Modal Price')}/क्विंटल\n"
            )

        return {
            "crop":        crop,
            "best_market": best.get("Market"),
            "best_price":  best.get("Modal Price"),
            "all_records": records[:5],
            "response_hi": response_hi,
            "success":     True,
        }

    except Exception as e:
        return _error_response(crop, "मंडी भाव लाने में समस्या हुई।")