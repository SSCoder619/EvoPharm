"""Unit tests for Purchase bounded context value objects."""
from __future__ import annotations

from decimal import Decimal
from unittest import TestCase
from uuid import UUID, uuid4

from evopharm_retail_erp.domain.purchase import (
    Discount,
    InvalidInvoiceReferenceError,
    InvalidPurchasePriceError,
    InvalidPurchaseQuantityError,
    InvalidSupplierReferenceError,
    InvoiceReference,
    Money,
    PurchaseId,
    PurchaseLineId,
    PurchaseOrderReference,
    PurchaseQuantity,
    PurchaseTotal,
    SupplierReference,
    TaxRate,
    UnitPrice,
)


class PurchaseValueObjectsTests(TestCase):
    def test_purchase_id_generation_and_string(self) -> None:
        p_id = PurchaseId.generate()
        self.assertIsInstance(p_id.value, UUID)
        self.assertEqual(str(p_id), str(p_id.value))

        from_str = PurchaseId.from_string(str(p_id.value))
        self.assertEqual(p_id, from_str)

    def test_supplier_reference_valid_and_invalid(self) -> None:
        s_id = uuid4()
        supplier_ref = SupplierReference.of(s_id, code="SUP-001", name="Pharma Supplies Inc")
        self.assertEqual(supplier_ref.supplier_id, s_id)
        self.assertEqual(supplier_ref.code, "SUP-001")
        self.assertEqual(supplier_ref.name, "Pharma Supplies Inc")
        self.assertIn("Pharma Supplies Inc", str(supplier_ref))

        with self.assertRaises(InvalidSupplierReferenceError):
            SupplierReference(supplier_id="invalid-uuid")  # type: ignore

        with self.assertRaises(InvalidSupplierReferenceError):
            SupplierReference.of(s_id, code="   ")

    def test_purchase_order_reference_normalization(self) -> None:
        po_ref = PurchaseOrderReference("  PO-2026-001  ")
        self.assertEqual(po_ref.value, "PO-2026-001")
        self.assertEqual(str(po_ref), "PO-2026-001")

        with self.assertRaises(InvalidSupplierReferenceError):
            PurchaseOrderReference("   ")

    def test_invoice_reference_normalization(self) -> None:
        inv_ref = InvoiceReference("  INV-998877  ")
        self.assertEqual(inv_ref.value, "INV-998877")
        self.assertEqual(str(inv_ref), "INV-998877")

        with self.assertRaises(InvalidInvoiceReferenceError):
            InvoiceReference("   ")

    def test_purchase_quantity_invariants_and_arithmetic(self) -> None:
        q = PurchaseQuantity(10)
        self.assertEqual(q.value, 10)
        self.assertTrue(q.is_positive())
        self.assertFalse(q.is_zero())

        q2 = q.add(5)
        self.assertEqual(q2.value, 15)

        q3 = q.subtract(3)
        self.assertEqual(q3.value, 7)

        with self.assertRaises(InvalidPurchaseQuantityError):
            q.subtract(20)

        with self.assertRaises(InvalidPurchaseQuantityError):
            PurchaseQuantity(-5)

        with self.assertRaises(InvalidPurchaseQuantityError):
            PurchaseQuantity("10")  # type: ignore

    def test_money_decimal_precision_and_arithmetic(self) -> None:
        m1 = Money.of("100.50")
        m2 = Money.of("50.25")

        self.assertEqual(m1.amount, Decimal("100.50"))
        self.assertEqual(m1.currency, "INR")

        added = m1.add(m2)
        self.assertEqual(added.amount, Decimal("150.75"))

        subtracted = m1.subtract(m2)
        self.assertEqual(subtracted.amount, Decimal("50.25"))

        multiplied = m1.multiply(2)
        self.assertEqual(multiplied.amount, Decimal("201.00"))

        with self.assertRaises(InvalidPurchasePriceError):
            Money.of("-10.00")

        with self.assertRaises(InvalidPurchasePriceError):
            m2.subtract(m1)

    def test_unit_price(self) -> None:
        up = UnitPrice.of("25.00")
        self.assertEqual(up.amount, Decimal("25.00"))

        total_cost = up.multiply(PurchaseQuantity(4))
        self.assertEqual(total_cost.amount, Decimal("100.00"))

    def test_discount_percentage_and_fixed(self) -> None:
        disc_pct = Discount.percent(10)
        base = Money.of("100.00")
        self.assertEqual(disc_pct.calculate_discount_amount(base).amount, Decimal("10.00"))

        disc_fixed = Discount.fixed("15.00")
        self.assertEqual(disc_fixed.calculate_discount_amount(base).amount, Decimal("15.00"))

        with self.assertRaises(InvalidPurchasePriceError):
            Discount.percent(150)

    def test_tax_rate_gst_calculation(self) -> None:
        tax_rate = TaxRate.of(18)  # 18% GST
        taxable = Money.of("1000.00")
        tax_amount = tax_rate.calculate_tax_amount(taxable)
        self.assertEqual(tax_amount.amount, Decimal("180.00"))

    def test_purchase_total_calculation(self) -> None:
        subtotal = Money.of("1000.00")
        discount = Money.of("100.00")
        tax = Money.of("162.00")

        total = PurchaseTotal.create(
            subtotal=subtotal,
            total_discount=discount,
            total_tax=tax,
        )

        self.assertEqual(total.subtotal.amount, Decimal("1000.00"))
        self.assertEqual(total.total_discount.amount, Decimal("100.00"))
        self.assertEqual(total.taxable_amount.amount, Decimal("900.00"))
        self.assertEqual(total.total_tax.amount, Decimal("162.00"))
        self.assertEqual(total.net_total.amount, Decimal("1062.00"))
