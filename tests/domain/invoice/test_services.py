"""Unit tests for Invoice domain services."""
from __future__ import annotations

from decimal import Decimal
from unittest import TestCase

from evopharm_retail_erp.domain.invoice import (
    Invoice,
    InvoiceQuantity,
    InvoiceTaxCalculationService,
    TaxRate,
    TaxType,
    UnitPrice,
)
from evopharm_retail_erp.domain.medicine import MedicineId


class InvoiceServicesTests(TestCase):
    def setUp(self) -> None:
        self.service = InvoiceTaxCalculationService()
        self.med_1 = MedicineId.generate()

    def test_summarize_tax_liabilities_across_invoices(self) -> None:
        # Invoice 1 (Intra-state): 10 units @ Rs 100.00, GST 18% -> 180 total tax (90 CGST + 90 SGST)
        inv1 = Invoice.create(tax_type=TaxType.INTRA_STATE)
        inv1.add_line(
            medicine_id=self.med_1,
            quantity=InvoiceQuantity(10),
            unit_price=UnitPrice.of("100.00"),
            tax_rate=TaxRate.of("18.00"),
        )

        # Invoice 2 (Inter-state): 5 units @ Rs 200.00, GST 12% -> 120 total tax (120 IGST)
        inv2 = Invoice.create(tax_type=TaxType.INTER_STATE)
        inv2.add_line(
            medicine_id=self.med_1,
            quantity=InvoiceQuantity(5),
            unit_price=UnitPrice.of("200.00"),
            tax_rate=TaxRate.of("12.00"),
        )

        summary = self.service.summarize_tax_liabilities([inv1, inv2])
        self.assertEqual(summary.subtotal.amount, Decimal("2000.00"))
        self.assertEqual(summary.cgst_amount.amount, Decimal("90.00"))
        self.assertEqual(summary.sgst_amount.amount, Decimal("90.00"))
        self.assertEqual(summary.igst_amount.amount, Decimal("120.00"))
        self.assertEqual(summary.total_tax.amount, Decimal("300.00"))
        self.assertEqual(summary.net_total.amount, Decimal("2300.00"))
