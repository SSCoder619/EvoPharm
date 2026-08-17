"""Unit tests for Inventory specifications."""
from __future__ import annotations

from unittest import TestCase

from evopharm_retail_erp.domain.inventory import (
    CanReserveStockSpecification,
    HasAvailableStockSpecification,
    HasReservedStockSpecification,
    Inventory,
    IsLowStockSpecification,
    IsOutOfStockSpecification,
    IsOverstockedSpecification,
    IsStockSufficientSpecification,
    MovementQuantity,
    NeedsReorderSpecification,
    OverstockSpecification,
    Quantity,
    StockThresholds,
)
from evopharm_retail_erp.domain.medicine import MedicineBatchId, MedicineId


class InventorySpecificationsTests(TestCase):
    def setUp(self) -> None:
        self.medicine_id = MedicineId.generate()
        self.batch_id = MedicineBatchId.generate()
        self.inventory = Inventory.create(
            medicine_id=self.medicine_id,
            medicine_batch_id=self.batch_id,
            initial_quantity=Quantity(50),
            thresholds=StockThresholds.create(
                reorder_level=Quantity(20),
                overstock_level=Quantity(100),
                minimum_level=Quantity(5),
            ),
        )

    def test_has_available_stock_specification(self) -> None:
        spec = HasAvailableStockSpecification()
        self.assertTrue(spec.is_satisfied_by(self.inventory))

        empty_inventory = Inventory.create(
            medicine_id=self.medicine_id,
            medicine_batch_id=MedicineBatchId.generate(),
            initial_quantity=Quantity(0),
        )
        self.assertFalse(spec.is_satisfied_by(empty_inventory))

    def test_has_reserved_stock_specification(self) -> None:
        spec = HasReservedStockSpecification()
        self.assertFalse(spec.is_satisfied_by(self.inventory))

        self.inventory.reserve_stock(MovementQuantity(10))
        self.assertTrue(spec.is_satisfied_by(self.inventory))

    def test_is_low_stock_and_needs_reorder_specifications(self) -> None:
        spec_low = IsLowStockSpecification()
        spec_reorder = NeedsReorderSpecification()

        self.assertFalse(spec_low.is_satisfied_by(self.inventory))
        self.assertFalse(spec_reorder.is_satisfied_by(self.inventory))

        self.inventory.record_dispense(MovementQuantity(35))  # on-hand drops to 15 (reorder level=20)
        self.assertTrue(spec_low.is_satisfied_by(self.inventory))
        self.assertTrue(spec_reorder.is_satisfied_by(self.inventory))

    def test_is_out_of_stock_specification(self) -> None:
        spec = IsOutOfStockSpecification()
        self.assertFalse(spec.is_satisfied_by(self.inventory))

        self.inventory.record_dispense(MovementQuantity(50))
        self.assertTrue(spec.is_satisfied_by(self.inventory))

    def test_is_overstocked_specification(self) -> None:
        spec_overstock = IsOverstockedSpecification()
        spec_overstock_alias = OverstockSpecification()

        self.assertFalse(spec_overstock.is_satisfied_by(self.inventory))

        self.inventory.record_receipt(MovementQuantity(100))  # on-hand becomes 150 (> 100)
        self.assertTrue(spec_overstock.is_satisfied_by(self.inventory))
        self.assertTrue(spec_overstock_alias.is_satisfied_by(self.inventory))

    def test_is_stock_sufficient_and_can_reserve_specifications(self) -> None:
        spec_sufficient = IsStockSufficientSpecification(Quantity(40))
        spec_can_reserve = CanReserveStockSpecification(Quantity(40))

        self.assertTrue(spec_sufficient.is_satisfied_by(self.inventory))
        self.assertTrue(spec_can_reserve.is_satisfied_by(self.inventory))

        spec_excess = IsStockSufficientSpecification(Quantity(100))
        self.assertFalse(spec_excess.is_satisfied_by(self.inventory))

    def test_specification_combinators(self) -> None:
        has_avail = HasAvailableStockSpecification()
        is_out = IsOutOfStockSpecification()

        combined_and = has_avail & (~is_out)
        self.assertTrue(combined_and.is_satisfied_by(self.inventory))

        combined_or = has_avail | is_out
        self.assertTrue(combined_or.is_satisfied_by(self.inventory))
