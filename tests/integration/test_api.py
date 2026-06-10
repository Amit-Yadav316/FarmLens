from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from farmlens.api.app import app
from farmlens.core.dependencies import get_mandi_service
from farmlens.features.mandi.exceptions import MandiException


@pytest.fixture
def client() -> TestClient:
    """Return a test client for the FastAPI app."""
    return TestClient(app, raise_server_exceptions=False)


class TestHealthEndpoints:
    """Integration tests for health check endpoints."""

    def test_health_returns_200(self, client: TestClient) -> None:
        """GET /health should return 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_ok(self, client: TestClient) -> None:
        """GET /health should return status ok."""
        response = client.get("/health")
        assert response.json()["status"] == "ok"


class TestSchemesEndpoint:
    """Integration tests for the /schemes endpoint (pure local data)."""

    def test_schemes_returns_200(self, client: TestClient) -> None:
        """GET /api/v1/schemes should return 200."""
        response = client.get("/api/v1/schemes", params={"query": "insurance"})
        assert response.status_code == 200

    def test_schemes_returns_matching_scheme(self, client: TestClient) -> None:
        """A query for insurance returns the crop insurance scheme."""
        response = client.get("/api/v1/schemes", params={"query": "crop insurance"})
        names = [s["name"] for s in response.json()["schemes"]]
        assert any("Bima" in name for name in names)

    def test_schemes_requires_query_param(self, client: TestClient) -> None:
        """Missing query param returns a 422 validation error."""
        response = client.get("/api/v1/schemes")
        assert response.status_code == 422


class TestExceptionHandling:
    """Integration tests for domain-exception -> HTTP status mapping."""

    def test_mandi_exception_maps_to_502(self, client: TestClient) -> None:
        """An upstream MandiException returns a clean 502, not a 500 traceback."""

        class _FailingMandi:
            def get_price(self, crop: str, state: str):
                raise MandiException("Agmarknet API timeout")

        app.dependency_overrides[get_mandi_service] = lambda: _FailingMandi()
        try:
            response = client.get("/api/v1/price", params={"crop": "Wheat", "state": "Punjab"})
        finally:
            app.dependency_overrides.clear()
        assert response.status_code == 502
        body = response.json()
        assert body["error"] == "MandiException"
        assert "timeout" in body["detail"]
