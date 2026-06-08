from __future__ import annotations

# Spray is unsafe above these thresholds
SPRAY_WIND_LIMIT_KMH: float = 15.0
SPRAY_RAIN_LIMIT_MM: float = 5.0
SPRAY_HUMIDITY_LIMIT_PCT: float = 90.0

# Major Indian state capitals with coordinates
STATE_CAPITALS: dict[str, tuple[float, float]] = {
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Bengaluru": (12.9716, 77.5946),
    "Hyderabad": (17.3850, 78.4867),
    "Chennai": (13.0827, 80.2707),
    "Kolkata": (22.5726, 88.3639),
    "Jaipur": (26.9124, 75.7873),
    "Lucknow": (26.8467, 80.9462),
    "Bhopal": (23.2599, 77.4126),
    "Patna": (25.5941, 85.1376),
}
