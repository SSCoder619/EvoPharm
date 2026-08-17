"""Unit tests for Sales bounded context value objects."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest import TestCase
from uuid import UUID, uuid4

from evopharm_retail_erp.domain.sales import (
    CustomerReference,
    Discount,
    InvalidCustomerReferenceError,
    InvalidInvoiceNumberError,
    InvalidPrescriptionReferenceError,
    InvalidSalePriceError,
    InvalidSaleQuantityError,
    InvoiceNumber,
    Money,
    PaymentReference,
    PrescriptionReference,
    SaleId,
    SaleLineId,
    SaleQuantity,
    SaleTotal,
    TaxRate,
    UnitPrice,
)


class SalesValueObjectsTests(TestCase):
    def test_sale_id_generation_and_string(self) -> None:
        s_id = SaleId.generate()
        self.assertIsInstance(s_id.value, UUID)
        self.assertEqual(str(s_id), str(s_id.value))

        from_str = SaleId.from_string(str(s_id.value))
        self.assertEqual(s_id, from_str)

    def test_customer_reference_walk_in_and_custom(self) -> None:
        walk_in = CustomerReference.walk_in()
        self.assertEqual(str(walk_in), "Walk-in Customer")

        c_id = uuid4()
        custom = CustomerReference.of(c_id, name="John Doe", phone="+919876543210")
        self.assertEqual(custom.customer_id, c_id)
        self.assertEqual(custom.name, "John Doe")
        self.assertEqual(custom.phone, "+919876543210")
        self.assertEqual(str(custom), "John Doe")

        with self.assertRaises(InvalidCustomerReferenceError):
            CustomerReference.of(c_id, name="   ")

    def test_invoice_number_normalization(self) -> None:
        inv = InvoiceNumber("  INV-2026-0001  ")
        self.assertEqual(inv.value, "INV-2026-0001")
        self.assertEqual(str(inv), "INV-2026-0001")

        with self.assertRaises(InvalidInvoiceNumberError):
            InvoiceNumber("   ")

    def test_prescription_reference_valid_and_invalid(self) -> None:
        rx = PrescriptionReference(
            prescription_number="RX-90812",
            doctor_name="Dr. A. Sharma",
            doctor_registration_number="REG-12345",
            prescription_date=date(2026, 8, 1),
        )
        self.assertEqual(rx.prescription_number, "RX-90812")
        self.assertEqual(rx.doctor_name, "Dr. A. Sharma")
        self.assertEqual(rx.doctor_registration_number, "REG-12345")
        self.assertIn("Rx#RX-90812", str(rx))

        with self.assertRaises(InvalidPrescriptionReferenceError):
            PrescriptionReference("", "Dr. Smith", "REG-1")

    def test_payment_reference(self) -> None:
        pay_ref = PaymentReference("TXN-UPI-992211")
        self.assertEqual(pay_ref.value, "TXN-UPI-992211")
        self.assertEqual(str(pay_ref), "TXN-UPI-992211")

    def test_sale_quantity_invariants_and_math(self) -> None:
        q = SaleQuantity(5)
        self.assertEqual(q.value, 5)
        self.assertTrue(q.is_positive())

        q2 = q.add(3)
        self.assertEqual(q2.value, 8)

        q3 = q.subtract(2)
        self.assertEqual(q3.value, 3)

        with self.assertRaises(InvalidSaleQuantityError):
            q.subtract(10)

        with self.assertRaises(InvalidSaleQuantityError):
            SaleQuantity(-1)

    def test_money_decimal_precision_and_arithmetic(self) -> None:
        m1 = Money.of("250.00")
        m2 = Money.of("100.00")

        self.assertEqual(m1.amount, Decimal("250.00"))
        self.assertEqual(m1.currency, "INR")

        self.assertEqual(m1.add(m2).amount, Decimal("350.00"))
        self.assertEqual(m1.subtract(m2).amount, Decimal("150.00"))
        self.assertEqual(m1.multiply(2).amount, Decimal("500.00"))

        with self.assertRaises(InvalidSalePriceError):
            Money.of("-5.00")

    def test_unit_price_and_discount_and_tax(self) -> None:
        up = UnitPrice.of("50.00")
        self.assertEqual(up.multiply(SaleQuantity(4)).amount, Decimal("200.00"))

        disc = Discount.percent(10)
        base = Money.of("200.00")
        self.assertEqual(disc.calculate_discount_amount(base).amount, Decimal("20.00"))

        tax = TaxRate.of(12)
        taxable = Money.of("180.00")
        self.assertEqual(tax.calculate_tax_amount(taxable).amount, Decimal("21.60"))

    def test_sale_total(self) -> None:
        subtotal = Money.of("500.00")
        discount = Money.of("50.00")
        tax = Money.of("54.00")

        total = SaleTotal.create(subtotal=subtotal, total_discount=discount, total_tax=tax)
        self.assertEqual(total.subtotal.amount, Decimal("500.00"))
        self.assertEqual(total.total_discount.amount, Decimal("50.00"))
        self.assertEqual(total.taxable_amount.amount, Decimal("450.00"))
        self.assertEqual(total.total_tax.amount, Decimal("54.00"))
        self.assertEqual(total.net_total.amount, Decimal("504.00"))
