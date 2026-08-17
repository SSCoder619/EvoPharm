"""Unit tests for Sale aggregate root and SaleLine entity."""
from __future__ import annotations

from dateutil.parser import parse
from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.domain.medicine import MedicineBatchId, MedicineId
from evopharm_retail_erp.domain.sales import (
    CustomerReference,
    Discount,
    ExceededSoldQuantityError,
    InvalidPaymentStateError,
    InvalidSaleLineError,
    InvalidSaleQuantityError,
    InvalidSaleStateError,
    InvoiceNumber,
    Money,
    PaymentMethod,
    PaymentStatus,
    PrescriptionReference,
    ReturnReason,
    Sale,
    SaleAlreadyCancelledError,
    SaleLineId,
    SaleNotCancellableError,
    SaleQuantity,
    SaleStatus,
    TaxRate,
    UnitPrice,
)


class SaleEntitiesTests(TestCase):
    def setUp(self) -> None:
        self.customer_ref = CustomerReference.walk_in()
        self.invoice_num = InvoiceNumber("INV-2026-1001")
        self.sale = Sale.create(
            customer_reference=self.customer_ref,
            invoice_number=self.invoice_num,
        )

        self.medicine_1 = MedicineId.generate()
        self.batch_1 = MedicineBatchId.generate()

    def test_create_initial_state(self) -> None:
        self.assertEqual(self.sale.sale_status, SaleStatus.DRAFT)
        self.assertEqual(self.sale.payment_status, PaymentStatus.UNPAID)
        self.assertEqual(len(self.sale.lines), 0)
        self.assertEqual(self.sale.customer_reference, self.customer_ref)
        self.assertEqual(self.sale.invoice_number, self.invoice_num)

    def test_add_and_remove_line(self) -> None:
        line1 = self.sale.add_line(
            medicine_id=self.medicine_1,
            batch_id=self.batch_1,
            quantity=SaleQuantity(10),
            unit_price=UnitPrice.of("20.00"),
            discount=Discount.percent(5),
            tax_rate=TaxRate.of(12),
        )

        self.assertEqual(len(self.sale.lines), 1)
        self.assertEqual(line1.medicine_id, self.medicine_1)
        self.assertEqual(line1.batch_id, self.batch_1)
        self.assertEqual(line1.quantity.value, 10)

        # Remove line
        self.sale.remove_line(line1.id)
        self.assertEqual(len(self.sale.lines), 0)

    def test_cannot_confirm_empty_sale(self) -> None:
        with self.assertRaises(InvalidSaleLineError):
            self.sale.confirm()

    def test_lifecycle_draft_to_confirmed_to_paid_to_completed(self) -> None:
        line = self.sale.add_line(
            medicine_id=self.medicine_1,
            quantity=SaleQuantity(2),
            unit_price=UnitPrice.of("100.00"),  # Net total 200.00
        )

        self.sale.confirm()
        self.assertEqual(self.sale.sale_status, SaleStatus.CONFIRMED)

        # Cannot add lines after confirmation
        with self.assertRaises(InvalidSaleStateError):
            self.sale.add_line(
                medicine_id=MedicineId.generate(),
                quantity=SaleQuantity(1),
                unit_price=UnitPrice.of("10.00"),
            )

        # Record payment
        self.sale.record_payment(
            amount_paid=Money.of("200.00"),
            payment_method=PaymentMethod.CASH,
        )
        self.assertEqual(self.sale.sale_status, SaleStatus.PAID)
        self.assertEqual(self.sale.payment_status, PaymentStatus.PAID)

        # Complete sale
        self.sale.complete()
        self.assertEqual(self.sale.sale_status, SaleStatus.COMPLETED)

    def test_prescription_attachment(self) -> None:
        rx = PrescriptionReference("RX-100", "Dr. A. Gupta", "REG-555")
        self.sale.attach_prescription(rx)
        self.assertEqual(self.sale.prescription_reference, rx)

    def test_process_return_and_refund(self) -> None:
        line = self.sale.add_line(
            medicine_id=self.medicine_1,
            quantity=SaleQuantity(10),
            unit_price=UnitPrice.of("50.00"),
        )
        self.sale.confirm()
        self.sale.record_payment(Money.of("500.00"))
        self.sale.complete()

        refund = self.sale.process_return(
            line_id=line.id,
            quantity=SaleQuantity(4),
            reason=ReturnReason.WRONG_MEDICINE,
        )

        self.assertEqual(refund.amount, Decimal("200.00"))
        self.assertEqual(line.returned_quantity.value, 4)
        self.assertEqual(line.net_quantity.value, 6)

        # Full return of remaining 6
        self.sale.process_return(line.id, SaleQuantity(6), ReturnReason.CUSTOMER_CHANGED_MIND)
        self.assertEqual(self.sale.sale_status, SaleStatus.RETURNED)
        self.assertEqual(self.sale.payment_status, PaymentStatus.REFUNDED)

    def test_exceeded_return_quantity_raises_error(self) -> None:
        line = self.sale.add_line(
            medicine_id=self.medicine_1,
            quantity=SaleQuantity(5),
            unit_price=UnitPrice.of("10.00"),
        )
        self.sale.confirm()
        self.sale.record_payment(Money.of("50.00"))
        self.sale.complete()

        with self.assertRaises(ExceededSoldQuantityError):
            self.sale.process_return(line.id, SaleQuantity(10))

    def test_cancel_sale_and_prevent_cancellation_if_completed(self) -> None:
        line = self.sale.add_line(
            medicine_id=self.medicine_1,
            quantity=SaleQuantity(5),
            unit_price=UnitPrice.of("10.00"),
        )
        self.sale.confirm()
        self.sale.cancel("Customer opted out")
        self.assertEqual(self.sale.sale_status, SaleStatus.CANCELLED)

        with self.assertRaises(SaleAlreadyCancelledError):
            self.sale.cancel("Duplicate cancel")

    def test_cannot_cancel_completed_sale(self) -> None:
        self.sale.add_line(
            medicine_id=self.medicine_1,
            quantity=SaleQuantity(1),
            unit_price=UnitPrice.of("10.00"),
        )
        self.sale.confirm()
        self.sale.record_payment(Money.of("10.00"))
        self.sale.complete()

        with self.assertRaises(SaleNotCancellableError):
            self.sale.cancel("Attempt cancel completed")
