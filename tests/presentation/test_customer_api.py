"""Tests for Customer API router."""
from __future__ import annotations

from unittest import TestCase
from uuid import uuid4
from fastapi.testclient import TestClient

from evopharm_retail_erp.presentation.api.app import create_app
from evopharm_retail_erp.presentation.api.dependencies import get_uow
from .helpers import InMemoryUnitOfWork


class CustomerApiTests(TestCase):
    def setUp(self) -> None:
        self.uow = InMemoryUnitOfWork()

        async def _override_uow():
            yield self.uow

        self.app = create_app()
        self.app.dependency_overrides[get_uow] = _override_uow
        self.client = TestClient(self.app)

    def test_register_get_and_update_customer(self) -> None:
        payload = {
            "name": "Rajesh Kumar",
            "phone": "9876543210",
            "email": "rajesh@example.com",
            "address": {
                "street": "M.G. Road",
                "city": "Bengaluru",
                "state": "Karnataka",
                "postal_code": "560001",
            },
        }

        res = self.client.post("/api/v1/customers", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["name"], "Rajesh Kumar")
        c_id = data["id"]

        get_res = self.client.get(f"/api/v1/customers/{c_id}")
        self.assertEqual(get_res.status_code, 200)

        upd_res = self.client.put(
            f"/api/v1/customers/{c_id}/contact",
            json={"phone": "9123456789", "email": "new.rajesh@example.com"},
        )
        self.assertEqual(upd_res.status_code, 200)
        self.assertEqual(upd_res.json()["phone"], "9123456789")
