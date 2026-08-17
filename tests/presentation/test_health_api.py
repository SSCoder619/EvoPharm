"""Tests for health check API endpoint."""
from __future__ import annotations

from unittest import TestCase
from fastapi.testclient import TestClient

from evopharm_retail_erp.presentation.api.app import create_app


class HealthApiTests(TestCase):
    def setUp(self) -> None:
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_health_check_endpoint(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
