"""Unit tests for InventoryApplicationService orchestration."""
from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
from types import TracebackType
from unittest import IsolatedAsyncioTestCase
from uuid import UUID, uuid4

from evopharm_retail_erp.application.common import UnitOfWork
from evopharm_retail_erp.application.inventory import (
    AdjustStockCommand,
    DispenseStockCommand,
    InventoryApplicationService,
    InventoryNotFoundError,
    ReceiveStockCommand,
    ReleaseStockCommand,
    ReserveStockCommand,
    TransferStockCommand,
    WriteOffStockCommand,
)
from evopharm_retail_erp.domain.inventory import (
    InsufficientStockError,
    Inventory,
    InventoryId,
    InventoryRepository,
    StockStatus,
)
from evopharm_retail_erp.domain.medicine import MedicineBatchId, MedicineId


class InMemoryInventoryRepository(InventoryRepository):
    def __init__(self) -> None:
        self.store: dict[InventoryId, Inventory] = {}

    def add(self, inventory: Inventory) -> None:
        if inventory.id in self.store:
            raise ValueError("Duplicate inventory ID")
        self.store[inventory.id] = deepcopy(inventory)

    def save(self, inventory: Inventory) -> None:
        if inventory.id not in self.store:
            raise KeyError("Inventory not found")
        self.store[inventory.id] = deepcopy(inventory)

    def get_by_id(self, inventory_id: InventoryId) -> Inventory | None:
        item = self.store.get(inventory_id)
        return deepcopy(item) if item else None

    def get_by_batch_id(self, batch_id: MedicineBatchId) -> Inventory | None:
        for item in self.store.values():
            if item.medicine_batch_id == batch_id:
                return deepcopy(item)
        return None

    def list_by_medicine_id(self, medicine_id: MedicineId) -> Sequence[Inventory]:
        return [deepcopy(item) for item in self.store.values() if item.medicine_id == medicine_id]

    def list_by_status(
        self, status: StockStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Inventory]:
        return [deepcopy(item) for item in self.store.values() if item.status == status]

    def list_low_stock(self, *, offset: int = 0, limit: int = 50) -> Sequence[Inventory]:
        return [deepcopy(item) for item in self.store.values() if item.is_low_stock]

    def list_out_of_stock(self, *, offset: int = 0, limit: int = 50) -> Sequence[Inventory]:
        return [deepcopy(item) for item in self.store.values() if item.is_out_of_stock]

    def list_overstocked(self, *, offset: int = 0, limit: int = 50) -> Sequence[Inventory]:
        return [deepcopy(item) for item in self.store.values() if item.status == StockStatus.OVERSTOCKED]

    def count_by_status(self, status: StockStatus) -> int:
        return sum(1 for item in self.store.values() if item.status == status)

    def exists(self, inventory_id: InventoryId) -> bool:
        return inventory_id in self.store

    def exists_for_batch(self, batch_id: MedicineBatchId) -> bool:
        return any(item.medicine_batch_id == batch_id for item in self.store.values())


class FakeUnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        self.inventory = InMemoryInventoryRepository()
        self.committed: bool = False
        self.rolled_back: bool = False

    async def __aenter__(self) -> FakeUnitOfWork:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


class InventoryApplicationServiceTests(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.uow = FakeUnitOfWork()
        self.service = InventoryApplicationService(self.uow)
        self.med_id = uuid4()
        self.batch_id = uuid4()

    async def test_receive_stock_use_case(self) -> None:
        cmd = ReceiveStockCommand(
            medicine_id=self.med_id,
            medicine_batch_id=self.batch_id,
            quantity=100,
            reason="Initial shipment receipt",
        )
        res = await self.service.receive_stock(cmd)

        self.assertTrue(res.is_success)
        self.assertTrue(self.uow.committed)
        self.assertEqual(res.value.quantity_on_hand, 100)
        self.assertEqual(res.value.quantity_available, 100)
        self.assertEqual(len(res.value.movements), 1)

    async def test_reserve_and_release_stock_use_case(self) -> None:
        rec_res = await self.service.receive_stock(
            ReceiveStockCommand(
                medicine_id=self.med_id,
                medicine_batch_id=self.batch_id,
                quantity=50,
            )
        )
        inv_id = rec_res.value.inventory_id

        # Reserve 10 units
        res_res = await self.service.reserve_stock(
            ReserveStockCommand(inventory_id=inv_id, quantity=10)
        )
        self.assertEqual(res_res.value.quantity_reserved, 10)
        self.assertEqual(res_res.value.quantity_available, 40)

        # Release 5 reserved units
        rel_res = await self.service.release_stock(
            ReleaseStockCommand(inventory_id=inv_id, quantity=5)
        )
        self.assertEqual(rel_res.value.quantity_reserved, 5)
        self.assertEqual(rel_res.value.quantity_available, 45)

    async def test_dispense_stock_use_case(self) -> None:
        rec_res = await self.service.receive_stock(
            ReceiveStockCommand(
                medicine_id=self.med_id,
                medicine_batch_id=self.batch_id,
                quantity=30,
            )
        )
        inv_id = rec_res.value.inventory_id

        disp_res = await self.service.dispense_stock(
            DispenseStockCommand(inventory_id=inv_id, quantity=10, reason="Retail sale dispensing")
        )
        self.assertEqual(disp_res.value.quantity_on_hand, 20)

    async def test_adjust_and_write_off_stock_use_case(self) -> None:
        rec_res = await self.service.receive_stock(
            ReceiveStockCommand(
                medicine_id=self.med_id,
                medicine_batch_id=self.batch_id,
                quantity=40,
            )
        )
        inv_id = rec_res.value.inventory_id

        # Positive adjustment
        adj_res = await self.service.adjust_stock(
            AdjustStockCommand(inventory_id=inv_id, quantity_delta=10, reason="Audit discrepancy add")
        )
        self.assertEqual(adj_res.value.quantity_on_hand, 50)

        # Write off stock
        wo_res = await self.service.write_off_stock(
            WriteOffStockCommand(inventory_id=inv_id, quantity=5, reason="Damaged in handling")
        )
        self.assertEqual(wo_res.value.quantity_on_hand, 45)

    async def test_transfer_stock_between_projections(self) -> None:
        batch2_id = uuid4()

        rec1 = await self.service.receive_stock(
            ReceiveStockCommand(
                medicine_id=self.med_id,
                medicine_batch_id=self.batch_id,
                quantity=50,
            )
        )
        rec2 = await self.service.receive_stock(
            ReceiveStockCommand(
                medicine_id=self.med_id,
                medicine_batch_id=batch2_id,
                quantity=10,
            )
        )

        from_id = rec1.value.inventory_id
        to_id = rec2.value.inventory_id

        trans_res = await self.service.transfer_stock(
            TransferStockCommand(
                from_inventory_id=from_id,
                to_inventory_id=to_id,
                quantity=15,
                reason="Batch transfer rebalance",
            )
        )

        res_from, res_to = trans_res.value
        self.assertEqual(res_from.quantity_on_hand, 35)
        self.assertEqual(res_to.quantity_on_hand, 25)

    async def test_insufficient_stock_error(self) -> None:
        rec_res = await self.service.receive_stock(
            ReceiveStockCommand(
                medicine_id=self.med_id,
                medicine_batch_id=self.batch_id,
                quantity=5,
            )
        )
        inv_id = rec_res.value.inventory_id

        with self.assertRaises(InsufficientStockError):
            await self.service.dispense_stock(
                DispenseStockCommand(inventory_id=inv_id, quantity=20)
            )

    async def test_inventory_not_found_error(self) -> None:
        missing_id = uuid4()
        with self.assertRaises(InventoryNotFoundError):
            await self.service.reserve_stock(
                ReserveStockCommand(inventory_id=missing_id, quantity=1)
            )
