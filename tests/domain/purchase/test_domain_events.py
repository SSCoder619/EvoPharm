"""Unit tests for Purchase bounded context domain events."""
from __future__ import annotations

from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.domain.medicine import MedicineId
from evopharm_retail_erp.domain.purchase import (
    InvoiceReference,
    Money,
    Purchase,
    PurchaseApproved,
    PurchaseCancelled,
    PurchaseCreated,
    PurchaseInvoiceAttached,
    PurchaseLineAdded,
    PurchaseOrdered,
    PurchaseOrderReference,
    PurchasePartiallyReceived,
    PurchasePaymentRecorded,
    PurchaseQuantity,
    PurchaseReceived,
    SupplierReference,
    UnitPrice,
)


class PurchaseDomainEventsTests(TestCase):
    def test_purchase_lifecycle_emits_expected_domain_events(self) -> None:
        supplier_ref = SupplierReference.of(uuid4())
        order_ref = PurchaseOrderReference("PO-EVENTS-01")

        # 1. PurchaseCreated
        purchase = Purchase.create(supplier_ref, order_ref)
        self.assertEqual(len(purchase.events), 1)
        self.assertIsInstance(purchase.events[0], PurchaseCreated)

        # 2. PurchaseLineAdded
        med_id = MedicineId.generate()
        line = purchase.add_line(
            medicine_id=med_id,
            ordered_quantity=PurchaseQuantity(20),
            unit_price=UnitPrice.of("10.00"),
        )
        self.assertEqual(len(purchase.events), 2)
        self.assertIsInstance(purchase.events[1], PurchaseLineAdded)

        # 3. PurchaseApproved
        purchase.approve()
        self.assertEqual(len(purchase.events), 3)
        self.assertIsInstance(purchase.events[2], PurchaseApproved)

        # 4. PurchaseOrdered
        purchase.place_order()
        self.assertEqual(len(purchase.events), 4)
        self.assertIsInstance(purchase.events[3], PurchaseOrdered)

        # 5. PurchasePartiallyReceived & PurchaseReceived
        purchase.receive_stock(line.id, PurchaseQuantity(20), "BATCH-X")
        self.assertEqual(len(purchase.events), 6)
        self.assertIsInstance(purchase.events[4], PurchaseReceived)
        self.assertIsInstance(purchase.events[5], PurchasePartiallyReceived)

        # 6. PurchaseInvoiceAttached & PurchasePaymentRecorded
        inv_ref = InvoiceReference("INV-001")
        purchase.attach_invoice(inv_ref)
        purchase.record_payment(Money.of("200.00"))

        events_types = [type(e) for e in purchase.events]
        self.assertIn(PurchaseInvoiceAttached, events_types)
        self.assertIn(PurchasePaymentRecorded, events_types)
