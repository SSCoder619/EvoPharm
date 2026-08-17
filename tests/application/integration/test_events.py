"""Unit tests for Application Integration event envelopes."""
from __future__ import annotations

from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.application.integration import (
    IntegrationEvent,
    InvoicePaidPayload,
    PurchaseReceivedPayload,
    SaleCompletedPayload,
    SaleReturnedPayload,
)


class IntegrationEventsTests(TestCase):
    def test_integration_event_creation(self) -> None:
        p_id = uuid4()
        l_id = uuid4()
        m_id = uuid4()

        payload = PurchaseReceivedPayload(
            purchase_id=p_id,
            line_id=l_id,
            medicine_id=m_id,
            received_quantity=50,
            batch_number="BATCH-001",
        )
        event = IntegrationEvent.create(
            source_context="purchase",
            event_type="PurchaseReceived",
            payload=payload,
        )

        self.assertEqual(event.source_context, "purchase")
        self.assertEqual(event.event_type, "PurchaseReceived")
        self.assertEqual(event.payload.received_quantity, 50)
        self.assertEqual(event.payload.batch_number, "BATCH-001")

    def test_sale_completed_and_returned_payloads(self) -> None:
        s_id = uuid4()
        l_id = uuid4()
        m_id = uuid4()

        comp_payload = SaleCompletedPayload(
            sale_id=s_id,
            invoice_number="INV-SALE-101",
            customer_name="Jane Doe",
        )
        ret_payload = SaleReturnedPayload(
            sale_id=s_id,
            line_id=l_id,
            medicine_id=m_id,
            returned_quantity=5,
            return_reason="Damaged box",
        )

        self.assertEqual(comp_payload.invoice_number, "INV-SALE-101")
        self.assertEqual(ret_payload.returned_quantity, 5)

    def test_invoice_paid_payload(self) -> None:
        i_id = uuid4()
        payload = InvoicePaidPayload(
            invoice_id=i_id,
            invoice_number="INV-2026-001",
            total_amount="1500.00",
        )
        self.assertEqual(payload.invoice_id, i_id)
        self.assertEqual(payload.total_amount, "1500.00")
