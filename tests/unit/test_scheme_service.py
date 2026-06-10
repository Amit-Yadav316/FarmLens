from __future__ import annotations

from farmlens.features.schemes.service import SchemeService


class TestSchemeService:
    """Tests for SchemeService keyword matching."""

    def test_find_schemes_returns_response_with_query(self, settings) -> None:
        """find_schemes echoes the original query in the response."""
        service = SchemeService(settings)
        result = service.find_schemes("insurance")
        assert result.query == "insurance"

    def test_find_schemes_matches_insurance(self, settings) -> None:
        """A query for insurance returns the Fasal Bima crop insurance scheme."""
        service = SchemeService(settings)
        result = service.find_schemes("crop insurance for failure")
        assert any("Bima" in s.name for s in result.schemes)

    def test_find_schemes_matches_credit(self, settings) -> None:
        """A query for credit returns the Kisan Credit Card scheme first."""
        service = SchemeService(settings)
        result = service.find_schemes("short-term credit loan")
        assert "Credit Card" in result.schemes[0].name

    def test_find_schemes_matches_income_support(self, settings) -> None:
        """A query for income support returns PM-KISAN."""
        service = SchemeService(settings)
        result = service.find_schemes("income support for farmers")
        assert result.schemes[0].name == "PM-KISAN"

    def test_find_schemes_falls_back_to_all_when_no_match(self, settings) -> None:
        """An unrelated query returns all schemes as a fallback."""
        service = SchemeService(settings)
        result = service.find_schemes("xyzabc nonsense")
        assert len(result.schemes) == 3

    def test_score_scheme_counts_matching_tokens(self, settings) -> None:
        """_score_scheme returns a higher score for more matching tokens."""
        service = SchemeService(settings)
        pm_kisan = service._schemes[0]
        high = service._score_scheme(pm_kisan, ["income", "support", "farmers"])
        low = service._score_scheme(pm_kisan, ["income"])
        assert high > low

    def test_score_scheme_zero_for_no_match(self, settings) -> None:
        """_score_scheme returns 0 when no tokens match."""
        service = SchemeService(settings)
        pm_kisan = service._schemes[0]
        assert service._score_scheme(pm_kisan, ["spaceship", "rocket"]) == 0

    def test_more_relevant_scheme_ranked_first(self, settings) -> None:
        """Schemes are sorted by relevance, most relevant first."""
        service = SchemeService(settings)
        result = service.find_schemes("insurance crop")
        assert "Bima" in result.schemes[0].name
