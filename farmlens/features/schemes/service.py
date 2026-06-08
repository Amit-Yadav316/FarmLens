from __future__ import annotations

from farmlens.core.config import Settings
from farmlens.features.schemes.data import SCHEMES
from farmlens.features.schemes.exceptions import SchemeException
from farmlens.features.schemes.schemas import Scheme, SchemeResponse


class SchemeService:
    """Looks up relevant government schemes by keyword matching."""

    def __init__(self, settings: Settings) -> None:
        self._schemes: list[Scheme] = SCHEMES

    def find_schemes(self, query: str) -> SchemeResponse:
        """Return schemes relevant to the given query."""
        raise NotImplementedError

    def _score_scheme(self, scheme: Scheme, query_tokens: list[str]) -> int:
        """Return a relevance score for a scheme against query tokens."""
        raise NotImplementedError
