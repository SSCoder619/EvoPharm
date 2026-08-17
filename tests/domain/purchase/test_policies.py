"""Unit tests for Purchase business policies and invariant constraints."""
from __future__ import annotations

from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.domain.medicine import MedicineId
from evopharm_retail_erp.domain.purchase import (
    DuplicatePurchaseLineError,
    InvalidPurchaseStateTransitionError,
    Purchase,
    PurchaseOrderReference,
    PurchaseQuantity,
    SupplierReference,
    UnitPrice,
)


class PurchasePoliciesTests(TestCase):
    def test_cannot_add_duplicate_medicine_line_to_same_purchase(self) -> None:
        supplier_ref = SupplierReference.of(uuid4())
        order_ref = PurchaseOrderReference("PO-POL-01")
        purchase = Purchase.create(supplier_ref, order_ref)
        med_id = MedicineId.generate()

        purchase.add_line(
            medicine_id=med_id,
            ordered_quantity=PurchaseQuantity(10),
            unit_price=UnitPrice.of("50.00"),
        )

        with self.assertRaises(DuplicatePurchaseLineError):
            purchase.add_line(
                medicine_id=med_id,
                ordered_quantity=PurchaseQuantity(20),
                unit_price=UnitPrice.of("50.00"),
            )

    def test_cannot_skip_approval_straight_to_ordered(self) -> None:
        supplier_ref = SupplierReference.of(uuid4())
        order_ref = PurchaseOrderReference("PO-POL-02")
        purchase = Purchase.create(supplier_ref, order_ref)

        with self.assertRaises(InvalidPurchaseStateTransitionError):
            purchase.place_order()
