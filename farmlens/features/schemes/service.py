from __future__ import annotations

from farmlens.features.schemes.data import SCHEMES
from farmlens.features.schemes.schemas import Scheme, SchemeResponse


class SchemeService:
    """Looks up relevant government schemes by keyword matching."""

    def __init__(self) -> None:
        self._schemes: list[Scheme] = SCHEMES

    def find_schemes(self, query: str) -> SchemeResponse:
        """Return schemes ranked by relevance to the given query."""
        tokens = query.lower().split()
        scored = [(self._score_scheme(s, tokens), s) for s in self._schemes]
        ranked = sorted(scored, key=lambda pair: pair[0], reverse=True)
        matched = [scheme for score, scheme in ranked if score > 0]
        results = matched if matched else self._schemes
        return SchemeResponse(schemes=results, query=query)

    def _score_scheme(self, scheme: Scheme, query_tokens: list[str]) -> int:
        """Return a relevance score for a scheme against query tokens."""
        haystack = " ".join(
            [
                scheme.name,
                scheme.name_hi,
                scheme.description,
                scheme.description_hi,
                scheme.eligibility,
                scheme.benefit,
            ]
        ).lower()
        return sum(1 for token in query_tokens if token in haystack)
