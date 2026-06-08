from __future__ import annotations

from farmlens.core.exceptions import FarmLensException


class ASRException(FarmLensException):
    """Raised when speech-to-text transcription fails."""
