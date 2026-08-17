"""Tests for Inventory API router."""
from __future__ import annotations

from unittest import TestCase
from uuid import uuid4
from fastapi.testclient import TestClient

from evopharm_retail_erp.presentation.api.app import create_app
from evopharm_retail_erp.presentation.api.dependencies import get_uow
from .helpers import InMemoryUnitOfWork


class InventoryApiTests(TestCase):
    def setUp(self) -> None:
        self.uow = InMemoryUnitOfWork()

        async def _override_uow():
            yield self.uow

        self.app = create_app()
        self.app.dependency_overrides[get_uow] = _override_uow
        self.client = TestClient(self.app)

    def test_receive_reserve_release_dispense_lifecycle(self) -> None:
        med_id = str(uuid4())
        batch_id = str(uuid4())

        # Receive stock
        rcv_payload = {
            "medicine_id": med_id,
            "medicine_batch_id": batch_id,
            "quantity": 100,
            "reason": "Initial GRN receipt",
        }
        res = self.client.post("/api/v1/inventory/receive", json=rcv_payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["quantity_on_hand"], 100)
        self.assertEqual(data["quantity_available"], 100)
        inv_id = data["id"]

        # Reserve stock
        resv_payload = {"inventory_id": inv_id, "quantity": 30}
        res_resv = self.client.post("/api/v1/inventory/reserve", json=resv_payload)
        self.assertEqual(res_resv.status_code, 200)
        data_resv = res_resv.json()
        self.assertEqual(data_resv["quantity_reserved"], 30)
        self.assertEqual(data_resv["quantity_available"], 70)

        # Release reservation
        rel_payload = {"inventory_id": inv_id, "quantity": 10}
        res_rel = self.client.post("/api/v1/inventory/release", json=rel_payload)
        self.assertEqual(res_rel.status_code, 200)
        self.assertEqual(res_rel.json()["quantity_reserved"], 20)

        # Dispense stock
        disp_payload = {"inventory_id": inv_id, "quantity": 20, "reason": "Counter sale"}
        res_disp = self.client.post("/api/v1/inventory/dispense", json=disp_payload)
        self.assertEqual(res_disp.status_code, 200)
        self.assertEqual(res_disp.json()["quantity_on_hand"], 80)
