"""Unit tests for Inventory domain services."""
from __future__ import annotations

from unittest import TestCase

from evopharm_retail_erp.domain.inventory import (
    Inventory,
    InventoryReconciliationService,
    MovementDirection,
    MovementQuantity,
    MovementType,
    Quantity,
    StockMovement,
    StockMovementId,
)
from evopharm_retail_erp.domain.medicine import MedicineBatchId, MedicineId


class InventoryServicesTests(TestCase):
    def setUp(self) -> None:
        self.medicine_id = MedicineId.generate()
        self.batch_id = MedicineBatchId.generate()
        self.service = InventoryReconciliationService()

    def test_reconciliation_consistent_ledger(self) -> None:
        inventory = Inventory.create(
            medicine_id=self.medicine_id,
            medicine_batch_id=self.batch_id,
            initial_quantity=Quantity(100),
        )

        m1 = StockMovement(
            id=StockMovementId.generate(),
            inventory_id=inventory.id,
            medicine_id=self.medicine_id,
            medicine_batch_id=self.batch_id,
            movement_type=MovementType.PURCHASE_RECEIPT,
            direction=MovementDirection.INBOUND,
            quantity=MovementQuantity(120),
        )
        m2 = StockMovement(
            id=StockMovementId.generate(),
            inventory_id=inventory.id,
            medicine_id=self.medicine_id,
            medicine_batch_id=self.batch_id,
            movement_type=MovementType.SALE_DISPENSE,
            direction=MovementDirection.OUTBOUND,
            quantity=MovementQuantity(20),
        )

        result = self.service.reconcile(inventory, [m1, m2])
        self.assertTrue(result.is_consistent)
        self.assertEqual(result.discrepancy, 0)
        self.assertEqual(result.expected_on_hand.value, 100)
        self.assertEqual(result.actual_on_hand.value, 100)

    def test_reconciliation_discrepancy_detected(self) -> None:
        inventory = Inventory.create(
            medicine_id=self.medicine_id,
            medicine_batch_id=self.batch_id,
            initial_quantity=Quantity(80),  # actual on-hand is 80
        )

        m1 = StockMovement(
            id=StockMovementId.generate(),
            inventory_id=inventory.id,
            medicine_id=self.medicine_id,
            medicine_batch_id=self.batch_id,
            movement_type=MovementType.PURCHASE_RECEIPT,
            direction=MovementDirection.INBOUND,
            quantity=MovementQuantity(100),  # expected on-hand is 100
        )

        result = self.service.reconcile(inventory, [m1])
        self.assertFalse(result.is_consistent)
        self.assertEqual(result.expected_on_hand.value, 100)
        self.assertEqual(result.actual_on_hand.value, 80)
        self.assertEqual(result.discrepancy, -20)
