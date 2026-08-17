"""Unit tests for Invoice domain events."""
from __future__ import annotations

from unittest import TestCase

from evopharm_retail_erp.domain.invoice import (
    Invoice,
    InvoiceCancelled,
    InvoiceCreated,
    InvoiceIssued,
    InvoiceLineAdded,
    InvoiceLineRemoved,
    InvoicePaid,
    InvoicePaymentRecorded,
    InvoiceQuantity,
    Money,
    UnitPrice,
)
from evopharm_retail_erp.domain.medicine import MedicineId


class InvoiceDomainEventsTests(TestCase):
    def test_invoice_events_emission(self) -> None:
        # 1. InvoiceCreated
        invoice = Invoice.create()
        self.assertEqual(len(invoice.events), 1)
        self.assertIsInstance(invoice.events[0], InvoiceCreated)

        # 2. InvoiceLineAdded
        med_id = MedicineId.generate()
        line = invoice.add_line(
            medicine_id=med_id,
            quantity=InvoiceQuantity(2),
            unit_price=UnitPrice.of("50.00"),
        )
        self.assertEqual(len(invoice.events), 2)
        self.assertIsInstance(invoice.events[1], InvoiceLineAdded)

        # 3. InvoiceLineRemoved
        invoice.remove_line(line.id)
        self.assertEqual(len(invoice.events), 3)
        self.assertIsInstance(invoice.events[2], InvoiceLineRemoved)

        # 4. InvoiceIssued
        invoice.add_line(
            medicine_id=med_id,
            quantity=InvoiceQuantity(1),
            unit_price=UnitPrice.of("100.00"),
        )
        invoice.issue()
        self.assertIsInstance(invoice.events[-1], InvoiceIssued)

        # 5. InvoicePaymentRecorded & InvoicePaid
        invoice.record_payment(Money.of("100.00"))
        self.assertIsInstance(invoice.events[-2], InvoicePaid)
        self.assertIsInstance(invoice.events[-1], InvoicePaymentRecorded)
