"""Unit tests for Inventory result DTOs."""
from __future__ import annotations

from unittest import TestCase

from evopharm_retail_erp.application.inventory import InventoryResult
from evopharm_retail_erp.domain.inventory import (
    Inventory,
    MovementQuantity,
    MovementReason,
)
from evopharm_retail_erp.domain.medicine import MedicineBatchId, MedicineId


class InventoryResultsTests(TestCase):
    def test_inventory_result_mapping_from_domain(self) -> None:
        med_id = MedicineId.generate()
        batch_id = MedicineBatchId.generate()
        inventory = Inventory.create(medicine_id=med_id, medicine_batch_id=batch_id)

        inventory.record_receipt(
            quantity=MovementQuantity(50),
            reason=MovementReason("Initial stock receipt"),
        )

        res = InventoryResult.from_domain(inventory)

        self.assertEqual(res.inventory_id, inventory.id.value)
        self.assertEqual(res.medicine_id, med_id.value)
        self.assertEqual(res.medicine_batch_id, batch_id.value)
        self.assertEqual(res.quantity_on_hand, 50)
        self.assertEqual(res.quantity_available, 50)
        self.assertEqual(res.status, "IN_STOCK")
        self.assertEqual(len(res.movements), 1)

        mv_res = res.movements[0]
        self.assertEqual(mv_res.movement_type, "PURCHASE_RECEIPT")
        self.assertEqual(mv_res.direction, "INBOUND")
        self.assertEqual(mv_res.quantity, 50)
        self.assertEqual(mv_res.signed_delta, 50)
        self.assertEqual(mv_res.reason, "Initial stock receipt")
