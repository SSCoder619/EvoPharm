"""Unit tests for Purchase aggregate <-> ORM mapping."""
from __future__ import annotations

from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.domain.medicine import MedicineId
from evopharm_retail_erp.domain.purchase import (
    Discount,
    InvoiceReference,
    Money,
    Purchase,
    PurchaseOrderReference,
    PurchaseQuantity,
    SupplierReference,
    TaxRate,
    UnitPrice,
)
from evopharm_retail_erp.infrastructure.persistence.mappers.purchase_mapper import (
    orm_to_purchase,
    purchase_to_orm,
)


class PurchaseMappingTests(TestCase):
    def test_roundtrip_purchase_mapping(self) -> None:
        sup_ref = SupplierReference.of(uuid4(), code="SUP-01", name="Apex Pharma")
        po_ref = PurchaseOrderReference("PO-2026-001")
        inv_ref = InvoiceReference("INV-2026-99")

        purchase = Purchase.create(
            supplier_reference=sup_ref,
            order_reference=po_ref,
            invoice_reference=inv_ref,
        )

        med_id = MedicineId.generate()
        purchase.add_line(
            medicine_id=med_id,
            ordered_quantity=PurchaseQuantity(50),
            unit_price=UnitPrice.of("100.00"),
            discount=Discount.percent("5.00"),
            tax_rate=TaxRate.of("12.00"),
        )
        purchase.approve()

        orm = purchase_to_orm(purchase)
        self.assertEqual(orm.order_reference, "PO-2026-001")
        self.assertEqual(len(orm.lines), 1)

        reconstructed = orm_to_purchase(orm)
        self.assertEqual(reconstructed.id, purchase.id)
        self.assertEqual(reconstructed.order_reference.value, "PO-2026-001")
        self.assertEqual(len(reconstructed.lines), 1)
        self.assertEqual(reconstructed.lines[0].medicine_id, med_id)
        self.assertEqual(reconstructed.lines[0].ordered_quantity.value, 50)
