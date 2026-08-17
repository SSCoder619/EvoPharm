"""Unit tests for Purchase bounded context specifications."""
from __future__ import annotations

from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.domain.medicine import MedicineId
from evopharm_retail_erp.domain.purchase import (
    CanCancelPurchaseSpecification,
    CanReceivePurchaseSpecification,
    HasOutstandingQuantitySpecification,
    IsPurchaseApprovedSpecification,
    IsPurchaseCancelledSpecification,
    IsPurchaseDraftSpecification,
    IsPurchaseOrderedSpecification,
    IsPurchaseReceivedSpecification,
    Purchase,
    PurchaseOrderReference,
    PurchaseQuantity,
    SupplierReference,
    UnitPrice,
)


class PurchaseSpecificationsTests(TestCase):
    def setUp(self) -> None:
        self.supplier_ref = SupplierReference.of(uuid4())
        self.order_ref = PurchaseOrderReference("PO-SPEC-01")
        self.purchase = Purchase.create(self.supplier_ref, self.order_ref)
        self.line = self.purchase.add_line(
            medicine_id=MedicineId.generate(),
            ordered_quantity=PurchaseQuantity(50),
            unit_price=UnitPrice.of("10.00"),
        )

    def test_draft_specification(self) -> None:
        spec = IsPurchaseDraftSpecification()
        self.assertTrue(spec.is_satisfied_by(self.purchase))

        self.purchase.approve()
        self.assertFalse(spec.is_satisfied_by(self.purchase))

    def test_approved_and_ordered_specifications(self) -> None:
        spec_approved = IsPurchaseApprovedSpecification()
        spec_ordered = IsPurchaseOrderedSpecification()

        self.assertFalse(spec_approved.is_satisfied_by(self.purchase))
        self.assertFalse(spec_ordered.is_satisfied_by(self.purchase))

        self.purchase.approve()
        self.assertTrue(spec_approved.is_satisfied_by(self.purchase))

        self.purchase.place_order()
        self.assertFalse(spec_approved.is_satisfied_by(self.purchase))
        self.assertTrue(spec_ordered.is_satisfied_by(self.purchase))

    def test_can_receive_specification(self) -> None:
        spec = CanReceivePurchaseSpecification()
        self.assertFalse(spec.is_satisfied_by(self.purchase))  # DRAFT cannot receive

        self.purchase.approve()
        self.assertFalse(spec.is_satisfied_by(self.purchase))  # APPROVED cannot receive until ORDERED

        self.purchase.place_order()
        self.assertTrue(spec.is_satisfied_by(self.purchase))  # ORDERED can receive

    def test_can_cancel_specification(self) -> None:
        spec = CanCancelPurchaseSpecification()
        self.assertTrue(spec.is_satisfied_by(self.purchase))

        self.purchase.approve()
        self.purchase.place_order()
        self.purchase.receive_stock(self.line.id, PurchaseQuantity(50), "B1")

        # Fully RECEIVED purchase cannot be cancelled
        self.assertFalse(spec.is_satisfied_by(self.purchase))

    def test_has_outstanding_quantity_specification(self) -> None:
        spec = HasOutstandingQuantitySpecification()
        self.assertTrue(spec.is_satisfied_by(self.line))

        self.purchase.approve()
        self.purchase.place_order()
        self.purchase.receive_stock(self.line.id, PurchaseQuantity(50), "B1")

        self.assertFalse(spec.is_satisfied_by(self.line))

    def test_composite_specifications(self) -> None:
        spec_draft = IsPurchaseDraftSpecification()
        spec_can_cancel = CanCancelPurchaseSpecification()

        combined = spec_draft & spec_can_cancel
        self.assertTrue(combined.is_satisfied_by(self.purchase))

        inverted = ~spec_draft
        self.assertFalse(inverted.is_satisfied_by(self.purchase))
