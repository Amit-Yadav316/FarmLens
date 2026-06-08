from __future__ import annotations

from farmlens.core.exceptions import FarmLensException


class MandiException(FarmLensException):
    """Raised when mandi price fetching fails."""
