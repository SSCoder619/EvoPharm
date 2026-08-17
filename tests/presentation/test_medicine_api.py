"""Tests for Medicine API router."""
from __future__ import annotations

from unittest import TestCase
from uuid import uuid4
from fastapi.testclient import TestClient

from evopharm_retail_erp.presentation.api.app import create_app
from evopharm_retail_erp.presentation.api.dependencies import get_uow
from .helpers import InMemoryUnitOfWork


class MedicineApiTests(TestCase):
    def setUp(self) -> None:
        self.uow = InMemoryUnitOfWork()

        async def _override_uow():
            yield self.uow

        self.app = create_app()
        self.app.dependency_overrides[get_uow] = _override_uow
        self.client = TestClient(self.app)

    def test_register_medicine_and_get_by_id(self) -> None:
        payload = {
            "name": "Augmentin 625",
            "generic_name": "Amoxicillin + Clavulanate",
            "composition": [
                {"ingredient": "Amoxicillin", "strength": 500, "unit": "MG"},
                {"ingredient": "Clavulanic Acid", "strength": 125, "unit": "MG"},
            ],
            "manufacturer": "GSK",
            "dosage_form": "TABLET",
            "pack_size": 10,
            "unit_of_measure": "TABLET",
            "hsn_code": "300490",
            "schedule": "SCHEDULE_H",
            "barcodes": ["8901234567890"],
            "alternate_names": ["Augmentin duo"],
        }

        response = self.client.post("/api/v1/medicines", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], "Augmentin 625")
        self.assertEqual(data["manufacturer"], "GSK")

        med_id = data["id"]
        get_res = self.client.get(f"/api/v1/medicines/{med_id}")
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.json()["name"], "Augmentin 625")

    def test_get_medicine_not_found_returns_404(self) -> None:
        random_id = uuid4()
        response = self.client.get(f"/api/v1/medicines/{random_id}")
        self.assertEqual(response.status_code, 404)
