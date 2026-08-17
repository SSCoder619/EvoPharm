"""Contract tests for Inventory repository ports."""
from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
from unittest import TestCase
from uuid import UUID

from evopharm_retail_erp.domain.inventory import (
    Inventory,
    InventoryId,
    InventoryRepository,
    Quantity,
    StockMovement,
    StockMovementId,
    StockMovementRepository,
    StockStatus,
)
from evopharm_retail_erp.domain.medicine import MedicineBatchId, MedicineId


class InMemoryInventoryRepository(InventoryRepository):
    """In-memory stub implementing InventoryRepository contract for testing."""

    def __init__(self) -> None:
        self._store: dict[InventoryId, Inventory] = {}

    def add(self, inventory: Inventory) -> None:
        if inventory.id in self._store:
            raise ValueError("Already exists")
        self._store[inventory.id] = deepcopy(inventory)

    def save(self, inventory: Inventory) -> None:
        if inventory.id not in self._store:
            raise KeyError("Not found")
        self._store[inventory.id] = deepcopy(inventory)

    def get_by_id(self, inventory_id: InventoryId) -> Inventory | None:
        item = self._store.get(inventory_id)
        return deepcopy(item) if item else None

    def get_by_batch_id(self, batch_id: MedicineBatchId) -> Inventory | None:
        for item in self._store.values():
            if item.medicine_batch_id == batch_id:
                return deepcopy(item)
        return None

    def list_by_medicine_id(self, medicine_id: MedicineId) -> Sequence[Inventory]:
        return [deepcopy(item) for item in self._store.values() if item.medicine_id == medicine_id]

    def list_by_status(
        self, status: StockStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Inventory]:
        return [deepcopy(item) for item in self._store.values() if item.status == status]

    def list_low_stock(self, *, offset: int = 0, limit: int = 50) -> Sequence[Inventory]:
        return [deepcopy(item) for item in self._store.values() if item.is_low_stock]

    def list_out_of_stock(self, *, offset: int = 0, limit: int = 50) -> Sequence[Inventory]:
        return [deepcopy(item) for item in self._store.values() if item.is_out_of_stock]

    def list_overstocked(self, *, offset: int = 0, limit: int = 50) -> Sequence[Inventory]:
        return [deepcopy(item) for item in self._store.values() if item.status == StockStatus.OVERSTOCKED]

    def count_by_status(self, status: StockStatus) -> int:
        return sum(1 for item in self._store.values() if item.status == status)

    def exists(self, inventory_id: InventoryId) -> bool:
        return inventory_id in self._store

    def exists_for_batch(self, batch_id: MedicineBatchId) -> bool:
        return any(item.medicine_batch_id == batch_id for item in self._store.values())


class InventoryRepositoryContractTests(TestCase):
    def setUp(self) -> None:
        self.repository = InMemoryInventoryRepository()
        self.medicine_id = MedicineId.generate()
        self.batch_id = MedicineBatchId.generate()
        self.inventory = Inventory.create(
            medicine_id=self.medicine_id,
            medicine_batch_id=self.batch_id,
            initial_quantity=Quantity(100),
        )

    def test_add_and_get_by_id(self) -> None:
        self.repository.add(self.inventory)
        retrieved = self.repository.get_by_id(self.inventory.id)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved, self.inventory)
        self.assertTrue(self.repository.exists(self.inventory.id))

    def test_get_by_batch_id_and_exists_for_batch(self) -> None:
        self.repository.add(self.inventory)
        retrieved = self.repository.get_by_batch_id(self.batch_id)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.medicine_batch_id, self.batch_id)
        self.assertTrue(self.repository.exists_for_batch(self.batch_id))

    def test_list_by_medicine_id(self) -> None:
        self.repository.add(self.inventory)
        items = self.repository.list_by_medicine_id(self.medicine_id)

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].medicine_id, self.medicine_id)
