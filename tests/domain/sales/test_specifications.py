"""Unit tests for Sales bounded context specifications."""
from __future__ import annotations

from unittest import TestCase

from evopharm_retail_erp.domain.medicine import MedicineId
from evopharm_retail_erp.domain.sales import (
    CanCancelSaleSpecification,
    CanConfirmSaleSpecification,
    HasOutstandingPaymentSpecification,
    HasReturnableQuantitySpecification,
    IsFullyPaidSpecification,
    IsSaleCancelledSpecification,
    IsSaleCompletedSpecification,
    IsSaleConfirmedSpecification,
    IsSaleDraftSpecification,
    Money,
    Sale,
    SaleQuantity,
    UnitPrice,
)


class SalesSpecificationsTests(TestCase):
    def setUp(self) -> None:
        self.sale = Sale.create()
        self.line = self.sale.add_line(
            medicine_id=MedicineId.generate(),
            quantity=SaleQuantity(10),
            unit_price=UnitPrice.of("20.00"),
        )

    def test_draft_specification(self) -> None:
        spec = IsSaleDraftSpecification()
        self.assertTrue(spec.is_satisfied_by(self.sale))

        self.sale.confirm()
        self.assertFalse(spec.is_satisfied_by(self.sale))

    def test_can_confirm_specification(self) -> None:
        spec = CanConfirmSaleSpecification()
        self.assertTrue(spec.is_satisfied_by(self.sale))

        self.sale.confirm()
        self.assertFalse(spec.is_satisfied_by(self.sale))

    def test_can_cancel_specification(self) -> None:
        spec = CanCancelSaleSpecification()
        self.assertTrue(spec.is_satisfied_by(self.sale))

        self.sale.confirm()
        self.sale.record_payment(Money.of("200.00"))
        self.sale.complete()
        self.assertFalse(spec.is_satisfied_by(self.sale))

    def test_payment_specifications(self) -> None:
        spec_outstanding = HasOutstandingPaymentSpecification()
        spec_paid = IsFullyPaidSpecification()

        self.assertTrue(spec_outstanding.is_satisfied_by(self.sale))
        self.assertFalse(spec_paid.is_satisfied_by(self.sale))

        self.sale.confirm()
        self.sale.record_payment(Money.of("200.00"))

        self.assertFalse(spec_outstanding.is_satisfied_by(self.sale))
        self.assertTrue(spec_paid.is_satisfied_by(self.sale))

    def test_has_returnable_quantity_specification(self) -> None:
        spec = HasReturnableQuantitySpecification()
        self.assertTrue(spec.is_satisfied_by(self.line))

        self.sale.confirm()
        self.sale.record_payment(Money.of("200.00"))
        self.sale.complete()
        self.sale.process_return(self.line.id, SaleQuantity(10))

        self.assertFalse(spec.is_satisfied_by(self.line))

    def test_composite_specifications(self) -> None:
        spec_draft = IsSaleDraftSpecification()
        spec_can_cancel = CanCancelSaleSpecification()

        combined = spec_draft & spec_can_cancel
        self.assertTrue(combined.is_satisfied_by(self.sale))

        inverted = ~spec_draft
        self.assertFalse(inverted.is_satisfied_by(self.sale))
