from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from farmlens.api.app import app


@pytest.fixture
def client() -> TestClient:
    """Return a test client for the FastAPI app."""
    return TestClient(app)


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
