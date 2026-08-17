"""Tests for Purchase API router."""
from __future__ import annotations

from unittest import TestCase
from uuid import uuid4
from fastapi.testclient import TestClient

from evopharm_retail_erp.presentation.api.app import create_app
from evopharm_retail_erp.presentation.api.dependencies import get_uow
from .helpers import InMemoryUnitOfWork


class PurchaseApiTests(TestCase):
    def setUp(self) -> None:
        self.uow = InMemoryUnitOfWork()

        async def _override_uow():
            yield self.uow

        self.app = create_app()
        self.app.dependency_overrides[get_uow] = _override_uow
        self.client = TestClient(self.app)

    def test_create_add_line_approve_purchase_flow(self) -> None:
        sup_id = str(uuid4())
        med_id = str(uuid4())

        po_payload = {
            "supplier_id": sup_id,
            "order_reference": "PO-API-2026-001",
            "supplier_name": "Torrent Pharma",
        }
        res = self.client.post("/api/v1/purchases", json=po_payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        po_id = data["id"]
        self.assertEqual(data["purchase_status"], "DRAFT")

        line_payload = {
            "medicine_id": med_id,
            "ordered_quantity": 100,
            "unit_price": 45.50,
            "discount_percentage": 5.0,
            "tax_rate_percentage": 12.0,
        }
        line_res = self.client.post(f"/api/v1/purchases/{po_id}/lines", json=line_payload)
        self.assertEqual(line_res.status_code, 200)
        self.assertEqual(len(line_res.json()["lines"]), 1)

        app_res = self.client.post(f"/api/v1/purchases/{po_id}/approve")
        self.assertEqual(app_res.status_code, 200)
        self.assertEqual(app_res.json()["purchase_status"], "APPROVED")
