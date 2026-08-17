"""Tests for Invoice API router."""
from __future__ import annotations

from decimal import Decimal
from unittest import TestCase
from uuid import uuid4
from fastapi.testclient import TestClient

from evopharm_retail_erp.presentation.api.app import create_app
from evopharm_retail_erp.presentation.api.dependencies import get_uow
from .helpers import InMemoryUnitOfWork


class InvoiceApiTests(TestCase):
    def setUp(self) -> None:
        self.uow = InMemoryUnitOfWork()

        async def _override_uow():
            yield self.uow

        self.app = create_app()
        self.app.dependency_overrides[get_uow] = _override_uow
        self.client = TestClient(self.app)

    def test_create_invoice_and_record_payment(self) -> None:
        cust_id = str(uuid4())
        doc_id = str(uuid4())
        med_id = str(uuid4())

        inv_payload = {
            "source_document_type": "SALE",
            "source_document_id": doc_id,
            "customer_id": cust_id,
            "due_days": 15,
        }
        res = self.client.post("/api/v1/invoices", json=inv_payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        inv_id = data["id"]

        line_payload = {
            "medicine_id": med_id,
            "ordered_quantity": 1,
            "unit_price": 500.00,
        }
        line_res = self.client.post(f"/api/v1/invoices/{inv_id}/lines", json=line_payload)
        self.assertEqual(line_res.status_code, 200)

        pay_payload = {
            "payment_amount": 500.00,
            "payment_method": "UPI",
            "reference_number": "UPI-REF-100200",
        }
        pay_res = self.client.post(f"/api/v1/invoices/{inv_id}/payments", json=pay_payload)
        self.assertEqual(pay_res.status_code, 200)
        self.assertEqual(Decimal(str(pay_res.json()["paid_amount"])), Decimal("500.00"))
