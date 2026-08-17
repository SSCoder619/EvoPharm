"""Unit tests for Invoice aggregate root and InvoiceLine entity."""
from __future__ import annotations

from decimal import Decimal
from unittest import TestCase

from evopharm_retail_erp.domain.invoice import (
    CustomerReference,
    DiscountAmount,
    DuplicateInvoiceLineError,
    InvalidInvoiceLineError,
    InvalidInvoiceStateError,
    Invoice,
    InvoiceAlreadyCancelledError,
    InvoiceLineNotFoundError,
    InvoiceQuantity,
    InvoiceStatus,
    Money,
    OverpaymentError,
    PaymentStatus,
    TaxRate,
    TaxType,
    UnitPrice,
)
from evopharm_retail_erp.domain.medicine import MedicineBatchId, MedicineId


class InvoiceEntitiesTests(TestCase):
    def setUp(self) -> None:
        self.invoice = Invoice.create(
            customer_reference=CustomerReference(name="John Smith"),
            tax_type=TaxType.INTRA_STATE,
        )
        self.med_1 = MedicineId.generate()
        self.med_2 = MedicineId.generate()

    def test_invoice_creation_initial_state(self) -> None:
        self.assertEqual(self.invoice.status, InvoiceStatus.DRAFT)
        self.assertEqual(self.invoice.payment_status, PaymentStatus.UNPAID)
        self.assertEqual(len(self.invoice.lines), 0)
        self.assertEqual(len(self.invoice.events), 1)

    def test_add_and_remove_line(self) -> None:
        line1 = self.invoice.add_line(
            medicine_id=self.med_1,
            quantity=InvoiceQuantity(10),
            unit_price=UnitPrice.of("50.00"),
            discount=DiscountAmount.percent("10.00"),
            tax_rate=TaxRate.of("18.00"),
        )
        self.assertEqual(len(self.invoice.lines), 1)
        self.assertEqual(line1.medicine_id, self.med_1)

        # Duplicate line check
        with self.assertRaises(DuplicateInvoiceLineError):
            self.invoice.add_line(
                medicine_id=self.med_1,
                quantity=InvoiceQuantity(5),
                unit_price=UnitPrice.of("50.00"),
            )

        self.invoice.remove_line(line1.id)
        self.assertEqual(len(self.invoice.lines), 0)

    def test_tax_and_totals_calculation(self) -> None:
        # Line 1: 10 units @ Rs 50.00 = 500 subtotal. 10% discount = 50. Taxable = 450.
        # Intra-state GST @ 18% on 450 = 81.00 total tax (40.50 CGST + 40.50 SGST). Net = 531.00.
        self.invoice.add_line(
            medicine_id=self.med_1,
            quantity=InvoiceQuantity(10),
            unit_price=UnitPrice.of("50.00"),
            discount=DiscountAmount.percent("10.00"),
            tax_rate=TaxRate.of("18.00"),
        )

        total = self.invoice.calculate_total()
        self.assertEqual(total.subtotal.amount, Decimal("500.00"))
        self.assertEqual(total.total_discount.amount, Decimal("50.00"))
        self.assertEqual(total.taxable_amount.amount, Decimal("450.00"))
        self.assertEqual(total.cgst_amount.amount, Decimal("40.50"))
        self.assertEqual(total.sgst_amount.amount, Decimal("40.50"))
        self.assertEqual(total.igst_amount.amount, Decimal("0.00"))
        self.assertEqual(total.total_tax.amount, Decimal("81.00"))
        self.assertEqual(total.net_total.amount, Decimal("531.00"))

    def test_issue_lifecycle(self) -> None:
        self.invoice.add_line(
            medicine_id=self.med_1,
            quantity=InvoiceQuantity(2),
            unit_price=UnitPrice.of("100.00"),
        )
        self.invoice.issue()
        self.assertEqual(self.invoice.status, InvoiceStatus.ISSUED)

        # Cannot add line after issuing
        with self.assertRaises(InvalidInvoiceStateError):
            self.invoice.add_line(
                medicine_id=self.med_2,
                quantity=InvoiceQuantity(1),
                unit_price=UnitPrice.of("10.00"),
            )

    def test_record_payments_and_completion(self) -> None:
        self.invoice.add_line(
            medicine_id=self.med_1,
            quantity=InvoiceQuantity(10),
            unit_price=UnitPrice.of("100.00"),
        )
        self.invoice.issue()

        # Partial payment
        self.invoice.record_payment(Money.of("400.00"))
        self.assertEqual(self.invoice.payment_status, PaymentStatus.PARTIALLY_PAID)

        # Overpayment rejection
        with self.assertRaises(OverpaymentError):
            self.invoice.record_payment(Money.of("700.00"))

        # Final payment completing the bill
        self.invoice.record_payment(Money.of("600.00"))
        self.assertEqual(self.invoice.payment_status, PaymentStatus.PAID)
        self.assertEqual(self.invoice.status, InvoiceStatus.PAID)

    def test_cancel_invoice(self) -> None:
        self.invoice.add_line(
            medicine_id=self.med_1,
            quantity=InvoiceQuantity(1),
            unit_price=UnitPrice.of("10.00"),
        )
        self.invoice.cancel("Customer cancelled purchase")
        self.assertEqual(self.invoice.status, InvoiceStatus.CANCELLED)

        with self.assertRaises(InvoiceAlreadyCancelledError):
            self.invoice.cancel("Double cancel")
