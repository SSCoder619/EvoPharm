"""Unit tests for Purchase aggregate root and PurchaseLine entity."""
from __future__ import annotations

from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.domain.medicine import MedicineId
from evopharm_retail_erp.domain.purchase import (
    Discount,
    ExceededOrderedQuantityError,
    InvalidInvoiceReferenceError,
    InvalidPurchaseLineError,
    InvalidPurchaseQuantityError,
    InvalidPurchaseStateTransitionError,
    InvoiceReference,
    Money,
    PaymentStatus,
    Purchase,
    PurchaseAlreadyCancelledError,
    PurchaseLineId,
    PurchaseNotCancellableError,
    PurchaseOrderReference,
    PurchaseQuantity,
    PurchaseStatus,
    ReceivingAgainstCancelledPurchaseError,
    ReceivingStatus,
    SupplierReference,
    TaxRate,
    UnitPrice,
)


class PurchaseEntitiesTests(TestCase):
    def setUp(self) -> None:
        self.supplier_ref = SupplierReference.of(uuid4(), code="SUP-01", name="Global Pharma")
        self.order_ref = PurchaseOrderReference("PO-2026-0001")
        self.purchase = Purchase.create(
            supplier_reference=self.supplier_ref,
            order_reference=self.order_ref,
        )

        self.medicine_1 = MedicineId.generate()
        self.medicine_2 = MedicineId.generate()

    def test_create_initial_state(self) -> None:
        self.assertEqual(self.purchase.purchase_status, PurchaseStatus.DRAFT)
        self.assertEqual(self.purchase.receiving_status, ReceivingStatus.PENDING)
        self.assertEqual(self.purchase.payment_status, PaymentStatus.UNPAID)
        self.assertEqual(len(self.purchase.lines), 0)
        self.assertEqual(self.purchase.supplier_reference, self.supplier_ref)
        self.assertEqual(self.purchase.order_reference, self.order_ref)

    def test_add_and_remove_line(self) -> None:
        line1 = self.purchase.add_line(
            medicine_id=self.medicine_1,
            ordered_quantity=PurchaseQuantity(100),
            unit_price=UnitPrice.of("50.00"),
            discount=Discount.percent(10),
            tax_rate=TaxRate.of(12),
        )

        self.assertEqual(len(self.purchase.lines), 1)
        self.assertEqual(line1.medicine_id, self.medicine_1)
        self.assertEqual(line1.ordered_quantity.value, 100)

        # Remove line
        self.purchase.remove_line(line1.id)
        self.assertEqual(len(self.purchase.lines), 0)

    def test_cannot_approve_empty_purchase(self) -> None:
        with self.assertRaises(InvalidPurchaseLineError):
            self.purchase.approve()

    def test_lifecycle_draft_to_approved_to_ordered(self) -> None:
        self.purchase.add_line(
            medicine_id=self.medicine_1,
            ordered_quantity=PurchaseQuantity(50),
            unit_price=UnitPrice.of("100.00"),
        )

        self.purchase.approve()
        self.assertEqual(self.purchase.purchase_status, PurchaseStatus.APPROVED)

        # Cannot add lines to approved purchase
        with self.assertRaises(InvalidPurchaseStateTransitionError):
            self.purchase.add_line(
                medicine_id=self.medicine_2,
                ordered_quantity=PurchaseQuantity(10),
                unit_price=UnitPrice.of("10.00"),
            )

        self.purchase.place_order()
        self.assertEqual(self.purchase.purchase_status, PurchaseStatus.ORDERED)

    def test_receive_stock_partial_and_complete(self) -> None:
        line = self.purchase.add_line(
            medicine_id=self.medicine_1,
            ordered_quantity=PurchaseQuantity(100),
            unit_price=UnitPrice.of("20.00"),
        )
        self.purchase.approve()
        self.purchase.place_order()

        # Receive 40 units (partial)
        self.purchase.receive_stock(
            line_id=line.id,
            quantity=PurchaseQuantity(40),
            batch_number="BATCH-001",
        )

        self.assertEqual(self.purchase.purchase_status, PurchaseStatus.PARTIALLY_RECEIVED)
        self.assertEqual(self.purchase.receiving_status, ReceivingStatus.PARTIAL)
        self.assertEqual(line.received_quantity.value, 40)
        self.assertEqual(line.outstanding_quantity.value, 60)

        # Receive remaining 60 units (completed)
        self.purchase.receive_stock(
            line_id=line.id,
            quantity=PurchaseQuantity(60),
            batch_number="BATCH-001",
        )

        self.assertEqual(self.purchase.purchase_status, PurchaseStatus.RECEIVED)
        self.assertEqual(self.purchase.receiving_status, ReceivingStatus.COMPLETED)
        self.assertTrue(line.is_fully_received)

    def test_exceeded_receiving_quantity_raises_error(self) -> None:
        line = self.purchase.add_line(
            medicine_id=self.medicine_1,
            ordered_quantity=PurchaseQuantity(50),
            unit_price=UnitPrice.of("10.00"),
        )
        self.purchase.approve()
        self.purchase.place_order()

        with self.assertRaises(ExceededOrderedQuantityError):
            self.purchase.receive_stock(
                line_id=line.id,
                quantity=PurchaseQuantity(60),
                batch_number="BATCH-001",
            )

    def test_cancel_purchase_and_prevent_receiving(self) -> None:
        line = self.purchase.add_line(
            medicine_id=self.medicine_1,
            ordered_quantity=PurchaseQuantity(50),
            unit_price=UnitPrice.of("10.00"),
        )
        self.purchase.approve()
        self.purchase.place_order()

        self.purchase.cancel("Supplier out of stock")
        self.assertEqual(self.purchase.purchase_status, PurchaseStatus.CANCELLED)

        with self.assertRaises(ReceivingAgainstCancelledPurchaseError):
            self.purchase.receive_stock(
                line_id=line.id,
                quantity=PurchaseQuantity(10),
                batch_number="BATCH-001",
            )

    def test_cannot_cancel_fully_received_purchase(self) -> None:
        line = self.purchase.add_line(
            medicine_id=self.medicine_1,
            ordered_quantity=PurchaseQuantity(10),
            unit_price=UnitPrice.of("10.00"),
        )
        self.purchase.approve()
        self.purchase.place_order()
        self.purchase.receive_stock(line.id, PurchaseQuantity(10), "BATCH-1")

        with self.assertRaises(PurchaseNotCancellableError):
            self.purchase.cancel("Too late")

    def test_attach_invoice_and_record_payment(self) -> None:
        line = self.purchase.add_line(
            medicine_id=self.medicine_1,
            ordered_quantity=PurchaseQuantity(10),
            unit_price=UnitPrice.of("100.00"),
        )
        self.purchase.approve()

        inv_ref = InvoiceReference("INV-2026-99")
        self.purchase.attach_invoice(inv_ref)
        self.assertEqual(self.purchase.invoice_reference, inv_ref)

        total = self.purchase.calculate_total()
        self.assertEqual(total.net_total.amount, Decimal("1000.00"))

        # Partial payment
        self.purchase.record_payment(Money.of("500.00"))
        self.assertEqual(self.purchase.payment_status, PaymentStatus.PARTIALLY_PAID)

        # Full payment
        self.purchase.record_payment(Money.of("500.00"))
        self.assertEqual(self.purchase.payment_status, PaymentStatus.PAID)

    def test_line_total_calculations(self) -> None:
        # Line: 10 units @ 100.00 each = 1000.00 subtotal
        # Discount: 10% = 100.00 discount -> 900.00 taxable
        # Tax: 18% GST on 900.00 = 162.00 tax
        # Net Total = 1062.00
        line = self.purchase.add_line(
            medicine_id=self.medicine_1,
            ordered_quantity=PurchaseQuantity(10),
            unit_price=UnitPrice.of("100.00"),
            discount=Discount.percent(10),
            tax_rate=TaxRate.of(18),
        )

        self.assertEqual(line.calculate_subtotal().amount, Decimal("1000.00"))
        self.assertEqual(line.calculate_discount_amount().amount, Decimal("100.00"))
        self.assertEqual(line.calculate_taxable_amount().amount, Decimal("900.00"))
        self.assertEqual(line.calculate_tax_amount().amount, Decimal("162.00"))
        self.assertEqual(line.calculate_line_total().amount, Decimal("1062.00"))

        total = self.purchase.calculate_total()
        self.assertEqual(total.net_total.amount, Decimal("1062.00"))
