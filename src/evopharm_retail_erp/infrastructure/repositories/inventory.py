"""SQLAlchemy implementation of the InventoryRepository protocol."""
from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from evopharm_retail_erp.domain.inventory import (
    Inventory,
    InventoryId,
    InventoryRepository,
    StockStatus,
)
from evopharm_retail_erp.domain.medicine import MedicineBatchId, MedicineId
from ..persistence.mappers.inventory_mapper import inventory_to_orm, orm_to_inventory
from ..persistence.models.inventory import InventoryORM

if TYPE_CHECKING:
    pass


class SqlAlchemyInventoryRepository(InventoryRepository):
    """SQLAlchemy 2.x persistence adapter for Inventory aggregate root."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, inventory: Inventory) -> None:
        """Persist a newly initialized inventory projection."""
        existing = self.session.get(InventoryORM, inventory.id.value)
        if existing is not None:
            raise ValueError(f"Inventory {inventory.id} already exists")

        orm = inventory_to_orm(inventory)
        self.session.add(orm)
        self.session.flush()

    def save(self, inventory: Inventory) -> None:
        """Persist changes to an existing inventory projection with optimistic locking."""
        existing = self.session.get(InventoryORM, inventory.id.value)
        if existing is None:
            raise KeyError(f"Inventory {inventory.id} does not exist")

        if inventory.version != existing.version + 1:
            raise ValueError(
                "Stale or invalid Inventory version; expected exactly one domain mutation"
            )

        new_orm = inventory_to_orm(inventory)
        self.session.merge(new_orm)
        self.session.flush()

    def get_by_id(self, inventory_id: InventoryId) -> Inventory | None:
        """Retrieve inventory projection by its primary ID."""
        stmt = (
            select(InventoryORM)
            .where(InventoryORM.id == inventory_id.value)
            .options(joinedload(InventoryORM.movements))
        )
        res = self.session.execute(stmt).unique().scalar_one_or_none()
        return orm_to_inventory(res) if res is not None else None

    def get_by_batch_id(self, batch_id: MedicineBatchId) -> Inventory | None:
        """Retrieve inventory projection for a specific medicine batch."""
        stmt = (
            select(InventoryORM)
            .where(InventoryORM.medicine_batch_id == batch_id.value)
            .options(joinedload(InventoryORM.movements))
        )
        res = self.session.execute(stmt).unique().scalar_one_or_none()
        return orm_to_inventory(res) if res is not None else None

    def list_by_medicine_id(self, medicine_id: MedicineId) -> Sequence[Inventory]:
        """All inventory projections belonging to a medicine product."""
        stmt = (
            select(InventoryORM)
            .where(InventoryORM.medicine_id == medicine_id.value)
            .options(joinedload(InventoryORM.movements))
        )
        rows = self.session.execute(stmt).unique().scalars().all()
        return tuple(orm_to_inventory(row) for row in rows)

    def list_by_status(
        self, status: StockStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Inventory]:
        """List inventory projections matching a specific stock status."""
        if offset < 0 or limit < 0:
            raise ValueError("offset and limit must not be negative")
        stmt = (
            select(InventoryORM)
            .options(joinedload(InventoryORM.movements))
            .offset(offset)
            .limit(limit)
        )
        rows = self.session.execute(stmt).unique().scalars().all()
        reconstructed = [orm_to_inventory(row) for row in rows]
        return tuple(inv for inv in reconstructed if inv.status == status)

    def list_low_stock(self, *, offset: int = 0, limit: int = 50) -> Sequence[Inventory]:
        """List inventory items where available quantity is at or below reorder level."""
        return self.list_by_status(StockStatus.LOW_STOCK, offset=offset, limit=limit)

    def list_out_of_stock(self, *, offset: int = 0, limit: int = 50) -> Sequence[Inventory]:
        """List inventory items where available quantity is zero."""
        return self.list_by_status(StockStatus.OUT_OF_STOCK, offset=offset, limit=limit)

    def list_overstocked(self, *, offset: int = 0, limit: int = 50) -> Sequence[Inventory]:
        """List inventory items where available quantity exceeds overstock level."""
        return self.list_by_status(StockStatus.OVERSTOCKED, offset=offset, limit=limit)

    def count_by_status(self, status: StockStatus) -> int:
        """Count inventory projections in a given status."""
        return len(self.list_by_status(status, offset=0, limit=10000))

    def exists(self, inventory_id: InventoryId) -> bool:
        """Check if an inventory projection exists by ID."""
        stmt = select(func.count(InventoryORM.id)).where(InventoryORM.id == inventory_id.value)
        return (self.session.execute(stmt).scalar() or 0) > 0

    def exists_for_batch(self, batch_id: MedicineBatchId) -> bool:
        """Check if an inventory projection already exists for a batch."""
        stmt = select(func.count(InventoryORM.id)).where(
            InventoryORM.medicine_batch_id == batch_id.value
        )
        return (self.session.execute(stmt).scalar() or 0) > 0
