"""Unit tests for Purchase result DTOs."""
from __future__ import annotations

from decimal import Decimal
from unittest import TestCase

from evopharm_retail_erp.application.purchase import PurchaseResult
from evopharm_retail_erp.domain.medicine import MedicineId
from evopharm_retail_erp.domain.purchase import (
    Discount,
    Purchase,
    PurchaseOrderReference,
    PurchaseQuantity,
    SupplierReference,
    TaxRate,
    UnitPrice,
)


from uuid import uuid4

class PurchaseResultsTests(TestCase):
    def test_purchase_result_mapping_from_domain(self) -> None:
        sup_id = uuid4()
        purchase = Purchase.create(
            supplier_reference=SupplierReference.of(sup_id),
            order_reference=PurchaseOrderReference("PO-9999"),
        )
        med_id = MedicineId.generate()
        purchase.add_line(
            medicine_id=med_id,
            ordered_quantity=PurchaseQuantity(10),
            unit_price=UnitPrice.of("100.00"),
            discount=Discount.percent("10.00"),
            tax_rate=TaxRate.of("18.00"),
        )

        res = PurchaseResult.from_domain(purchase)

        self.assertEqual(res.purchase_id, purchase.id.value)
        self.assertEqual(res.supplier_id, sup_id)
        self.assertEqual(res.order_reference, "PO-9999")
        self.assertEqual(res.purchase_status, "DRAFT")
        self.assertEqual(len(res.lines), 1)

        line_res = res.lines[0]
        self.assertEqual(line_res.medicine_id, med_id.value)
        self.assertEqual(line_res.ordered_quantity, 10)
        self.assertEqual(line_res.subtotal, Decimal("1000.00"))
        self.assertEqual(line_res.discount_amount, Decimal("100.00"))
        self.assertEqual(line_res.tax_amount, Decimal("162.00"))
        self.assertEqual(line_res.line_total, Decimal("1062.00"))
