"""Unit tests for Sales business policies and invariant constraints."""
from __future__ import annotations

from unittest import TestCase

from evopharm_retail_erp.domain.medicine import MedicineBatchId, MedicineId
from evopharm_retail_erp.domain.sales import (
    DuplicateSaleLineError,
    InvalidSaleStateError,
    Sale,
    SaleQuantity,
    UnitPrice,
)


class SalesPoliciesTests(TestCase):
    def test_cannot_add_duplicate_medicine_and_batch_line_to_same_sale(self) -> None:
        sale = Sale.create()
        med_id = MedicineId.generate()
        batch_id = MedicineBatchId.generate()

        sale.add_line(
            medicine_id=med_id,
            batch_id=batch_id,
            quantity=SaleQuantity(2),
            unit_price=UnitPrice.of("50.00"),
        )

        with self.assertRaises(DuplicateSaleLineError):
            sale.add_line(
                medicine_id=med_id,
                batch_id=batch_id,
                quantity=SaleQuantity(5),
                unit_price=UnitPrice.of("50.00"),
            )

    def test_cannot_skip_confirmation_straight_to_completed(self) -> None:
        sale = Sale.create()
        sale.add_line(
            medicine_id=MedicineId.generate(),
            quantity=SaleQuantity(1),
            unit_price=UnitPrice.of("10.00"),
        )

        with self.assertRaises(InvalidSaleStateError):
            sale.complete()
