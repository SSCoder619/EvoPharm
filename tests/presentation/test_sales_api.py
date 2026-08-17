"""Tests for Sales API router."""
from __future__ import annotations

from unittest import TestCase
from uuid import uuid4
from fastapi.testclient import TestClient

from evopharm_retail_erp.presentation.api.app import create_app
from evopharm_retail_erp.presentation.api.dependencies import get_uow
from .helpers import InMemoryUnitOfWork


class SalesApiTests(TestCase):
    def setUp(self) -> None:
        self.uow = InMemoryUnitOfWork()

        async def _override_uow():
            yield self.uow

        self.app = create_app()
        self.app.dependency_overrides[get_uow] = _override_uow
        self.client = TestClient(self.app)

    def test_create_sale_add_line_and_complete(self) -> None:
        cust_id = str(uuid4())
        med_id = str(uuid4())
        batch_id = str(uuid4())
        inv_id = str(uuid4())

        # Receive stock
        rcv_payload = {
            "medicine_id": med_id,
            "medicine_batch_id": batch_id,
            "quantity": 50,
            "inventory_id": inv_id,
        }
        self.client.post("/api/v1/inventory/receive", json=rcv_payload)

        # Create sale
        sale_res = self.client.post("/api/v1/sales", json={"customer_id": cust_id})
        self.assertEqual(sale_res.status_code, 201)
        sale_data = sale_res.json()
        sale_id = sale_data["id"]

        # Add line
        line_payload = {
            "medicine_id": med_id,
            "medicine_batch_id": batch_id,
            "inventory_id": inv_id,
            "quantity": 2,
            "unit_price": 150.00,
        }
        line_res = self.client.post(f"/api/v1/sales/{sale_id}/lines", json=line_payload)
        self.assertEqual(line_res.status_code, 200)
        self.assertEqual(len(line_res.json()["lines"]), 1)
