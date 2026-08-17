"""Unit tests for Sales result DTOs."""
from __future__ import annotations

from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.application.sales import SaleResult
from evopharm_retail_erp.domain.medicine import MedicineId
from evopharm_retail_erp.domain.sales import (
    CustomerReference,
    Discount,
    InvoiceNumber,
    PrescriptionReference,
    Sale,
    SaleQuantity,
    TaxRate,
    UnitPrice,
)


class SalesResultsTests(TestCase):
    def test_sale_result_mapping_from_domain(self) -> None:
        cust_id = uuid4()
        cust_ref = CustomerReference.of(customer_id=cust_id, name="John Doe", phone="9876543210")
        inv_num = InvoiceNumber("INV-2026-8888")
        rx_ref = PrescriptionReference("RX-001", "Dr. Rao", "MCI-4321")

        sale = Sale.create(
            customer_reference=cust_ref,
            invoice_number=inv_num,
            prescription_reference=rx_ref,
        )
        med_id = MedicineId.generate()
        sale.add_line(
            medicine_id=med_id,
            quantity=SaleQuantity(10),
            unit_price=UnitPrice.of("50.00"),
            discount=Discount.percent("10.00"),
            tax_rate=TaxRate.of("18.00"),
        )

        res = SaleResult.from_domain(sale)

        self.assertEqual(res.sale_id, sale.id.value)
        self.assertEqual(res.customer.customer_id, cust_id)
        self.assertEqual(res.customer.name, "John Doe")
        self.assertEqual(res.invoice_number, "INV-2026-8888")
        self.assertIsNotNone(res.prescription)
        self.assertEqual(res.prescription.prescription_number, "RX-001")
        self.assertEqual(res.sale_status, "DRAFT")
        self.assertEqual(len(res.lines), 1)

        line_res = res.lines[0]
        self.assertEqual(line_res.medicine_id, med_id.value)
        self.assertEqual(line_res.quantity, 10)
        self.assertEqual(line_res.subtotal, Decimal("500.00"))
        self.assertEqual(line_res.discount_amount, Decimal("50.00"))
        self.assertEqual(line_res.tax_amount, Decimal("81.00"))
        self.assertEqual(line_res.line_total, Decimal("531.00"))
