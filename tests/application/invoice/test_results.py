"""Unit tests for Invoice result DTOs."""
from __future__ import annotations

from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.application.invoice import InvoiceResult
from evopharm_retail_erp.domain.invoice import (
    CustomerReference,
    DiscountAmount,
    Invoice,
    InvoiceNumber,
    InvoiceQuantity,
    InvoiceType,
    SaleReference,
    TaxRate,
    TaxType,
    UnitPrice,
)
from evopharm_retail_erp.domain.medicine import MedicineId


class InvoiceResultsTests(TestCase):
    def test_intra_state_invoice_result_gst_mapping(self) -> None:
        sale_id = uuid4()
        sale_ref = SaleReference(sale_id=sale_id, sale_invoice_number="SALE-101")
        cust_ref = CustomerReference(name="Apollo Med", gstin="27AAAAA0000A1Z5")
        inv_num = InvoiceNumber("INV-2026-9999")

        invoice = Invoice.create(
            number=inv_num,
            sale_reference=sale_ref,
            customer_reference=cust_ref,
            invoice_type=InvoiceType.TAX_INVOICE,
            tax_type=TaxType.INTRA_STATE,
        )
        med_id = MedicineId.generate()
        invoice.add_line(
            medicine_id=med_id,
            quantity=InvoiceQuantity(10),
            unit_price=UnitPrice.of("100.00"),
            discount=DiscountAmount.percent("10.00"),
            tax_rate=TaxRate.of("18.00"),
        )

        res = InvoiceResult.from_domain(invoice)

        self.assertEqual(res.invoice_id, invoice.id.value)
        self.assertEqual(res.number, "INV-2026-9999")
        self.assertIsNotNone(res.sale_reference)
        self.assertEqual(res.sale_reference.sale_id, sale_id)
        self.assertEqual(res.tax_type, "INTRA_STATE")
        self.assertEqual(res.status, "DRAFT")

        # Total checks: Subtotal=1000, Disc=100 -> Taxable=900. Tax=18% of 900 = 162. CGST=81, SGST=81. Net=1062
        self.assertEqual(res.total.subtotal, Decimal("1000.00"))
        self.assertEqual(res.total.total_discount, Decimal("100.00"))
        self.assertEqual(res.total.taxable_amount, Decimal("900.00"))
        self.assertEqual(res.total.cgst_amount, Decimal("81.00"))
        self.assertEqual(res.total.sgst_amount, Decimal("81.00"))
        self.assertEqual(res.total.igst_amount, Decimal("0.00"))
        self.assertEqual(res.total.total_tax, Decimal("162.00"))
        self.assertEqual(res.total.net_total, Decimal("1062.00"))

    def test_inter_state_invoice_result_igst_mapping(self) -> None:
        invoice = Invoice.create(
            number=InvoiceNumber("INV-INTER-01"),
            tax_type=TaxType.INTER_STATE,
        )
        med_id = MedicineId.generate()
        invoice.add_line(
            medicine_id=med_id,
            quantity=InvoiceQuantity(5),
            unit_price=UnitPrice.of("200.00"),
            tax_rate=TaxRate.of("12.00"),
        )

        res = InvoiceResult.from_domain(invoice)

        self.assertEqual(res.tax_type, "INTER_STATE")
        self.assertEqual(res.total.subtotal, Decimal("1000.00"))
        self.assertEqual(res.total.cgst_amount, Decimal("0.00"))
        self.assertEqual(res.total.sgst_amount, Decimal("0.00"))
        self.assertEqual(res.total.igst_amount, Decimal("120.00"))
        self.assertEqual(res.total.total_tax, Decimal("120.00"))
        self.assertEqual(res.total.net_total, Decimal("1120.00"))
