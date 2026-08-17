"""Unit tests for Inventory aggregate <-> ORM mapping."""
from __future__ import annotations

from unittest import TestCase

from evopharm_retail_erp.domain.inventory import (
    Inventory,
    MovementQuantity,
    Quantity,
    StockThresholds,
)
from evopharm_retail_erp.domain.medicine import MedicineBatchId, MedicineId
from evopharm_retail_erp.infrastructure.persistence.mappers.inventory_mapper import (
    inventory_to_orm,
    orm_to_inventory,
)


class InventoryMappingTests(TestCase):
    def test_roundtrip_inventory_mapping(self) -> None:
        m_id = MedicineId.generate()
        b_id = MedicineBatchId.generate()
        thresholds = StockThresholds.create(
            reorder_level=20,
            overstock_level=80,
            minimum_level=10,
        )
        inv = Inventory.create(
            medicine_id=m_id,
            medicine_batch_id=b_id,
            initial_quantity=Quantity(50),
            thresholds=thresholds,
        )
        inv.record_receipt(MovementQuantity(10), reason=None)

        orm = inventory_to_orm(inv)
        self.assertEqual(orm.quantity_on_hand, 60)
        self.assertEqual(len(orm.movements), 1)

        reconstructed = orm_to_inventory(orm)
        self.assertEqual(reconstructed.id, inv.id)
        self.assertEqual(reconstructed.medicine_id, m_id)
        self.assertEqual(reconstructed.medicine_batch_id, b_id)
        self.assertEqual(reconstructed.quantity_on_hand.value, 60)
        self.assertEqual(len(reconstructed.movements), 1)
