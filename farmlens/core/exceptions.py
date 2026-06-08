from __future__ import annotations


class FarmLensException(Exception):
    """Base exception for all FarmLens errors."""


class MandiException(FarmLensException):
    """Raised when mandi price fetching fails."""


class WeatherException(FarmLensException):
    """Raised when weather data fetching fails."""


class RAGException(FarmLensException):
    """Raised when RAG pipeline operations fail."""


class ASRException(FarmLensException):
    """Raised when speech-to-text transcription fails."""


class SchemeException(FarmLensException):
    """Raised when scheme lookup fails."""


class IntentException(FarmLensException):
    """Raised when intent routing fails."""
