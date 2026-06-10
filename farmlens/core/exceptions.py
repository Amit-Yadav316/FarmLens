from __future__ import annotations


class FarmLensException(Exception):
    """Base exception for all FarmLens errors.

    Feature-specific exceptions (MandiException, WeatherException, etc.) live in
    each feature's own exceptions.py and subclass this base.
    """
