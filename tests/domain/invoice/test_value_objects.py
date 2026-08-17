"""Unit tests for Invoice domain value objects."""
from __future__ import annotations

from decimal import Decimal
from unittest import TestCase
from uuid import UUID

from evopharm_retail_erp.domain.invoice import (
    CustomerReference,
    DiscountAmount,
    GstBreakdown,
    InvalidInvoiceAmountError,
    InvalidInvoiceNumberError,
    InvalidInvoiceQuantityError,
    InvalidTaxRateError,
    InvoiceId,
    InvoiceLineId,
    InvoiceNumber,
    InvoiceQuantity,
    Money,
    SaleReference,
    TaxRate,
    TaxType,
    UnitPrice,
)


class InvoiceValueObjectsTests(TestCase):
    def test_invoice_id_generation(self) -> None:
        inv_id = InvoiceId.generate()
        self.assertIsInstance(inv_id.value, UUID)
        self.assertEqual(str(inv_id), str(inv_id.value))

        line_id = InvoiceLineId.generate()
        self.assertIsInstance(line_id.value, UUID)

    def test_invoice_number_validation(self) -> None:
        inv_num = InvoiceNumber("  INV-2026-00001  ")
        self.assertEqual(inv_num.value, "INV-2026-00001")
        self.assertEqual(str(inv_num), "INV-2026-00001")

        with self.assertRaises(InvalidInvoiceNumberError):
            InvoiceNumber("   ")

    def test_money_decimal_arithmetic(self) -> None:
        m1 = Money.of("100.50")
        m2 = Money.of("49.50")

        m3 = m1.add(m2)
        self.assertEqual(m3.amount, Decimal("150.00"))

        m4 = m1.subtract(m2)
        self.assertEqual(m4.amount, Decimal("51.00"))

        m5 = m1.multiply(2)
        self.assertEqual(m5.amount, Decimal("201.00"))

        with self.assertRaises(InvalidInvoiceAmountError):
            Money.of("-10.00")

    def test_unit_price_multiply(self) -> None:
        up = UnitPrice.of("25.00")
        total = up.multiply(InvoiceQuantity(4))
        self.assertEqual(total.amount, Decimal("100.00"))

    def test_discount_amount_calculation(self) -> None:
        base = Money.of("200.00")
        disc_pct = DiscountAmount.percent("10.00")
        self.assertEqual(disc_pct.calculate_discount_amount(base).amount, Decimal("20.00"))

        disc_fixed = DiscountAmount.fixed("15.00")
        self.assertEqual(disc_fixed.calculate_discount_amount(base).amount, Decimal("15.00"))

    def test_gst_breakdown_intra_vs_inter_state(self) -> None:
        taxable = Money.of("1000.00")
        rate = TaxRate.of("18.00")

        # Intra-state: 9% CGST + 9% SGST
        intra_bd = GstBreakdown.calculate(taxable, rate, TaxType.INTRA_STATE)
        self.assertEqual(intra_bd.total_tax.amount, Decimal("180.00"))
        self.assertEqual(intra_bd.cgst.amount, Decimal("90.00"))
        self.assertEqual(intra_bd.sgst.amount, Decimal("90.00"))
        self.assertEqual(intra_bd.igst.amount, Decimal("0.00"))

        # Inter-state: 18% IGST
        inter_bd = GstBreakdown.calculate(taxable, rate, TaxType.INTER_STATE)
        self.assertEqual(inter_bd.total_tax.amount, Decimal("180.00"))
        self.assertEqual(inter_bd.cgst.amount, Decimal("0.00"))
        self.assertEqual(inter_bd.sgst.amount, Decimal("0.00"))
        self.assertEqual(inter_bd.igst.amount, Decimal("180.00"))

    def test_references(self) -> None:
        sale_ref = SaleReference(sale_id=UUID("12345678-1234-5678-1234-567812345678"), sale_invoice_number="INV-001")
        self.assertEqual(str(sale_ref), "Sale#INV-001")

        cust_ref = CustomerReference(name="Jane Doe", gstin="29ABCDE1234F1Z5")
        self.assertEqual(str(cust_ref), "Jane Doe")
