"""Repository interfaces (ports) for the Inventory domain.

These are pure contracts — no implementation, no ORM, no SQL. They define what
the Inventory domain requires from persistence; concrete adapters (SQL, in-memory, etc.)
live in the Infrastructure layer and satisfy these Protocols structurally.
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from ..medicine.value_objects import MedicineBatchId, MedicineId
from .entities import Inventory, StockMovement
from .enums import StockStatus
from .value_objects import InventoryId, StockMovementId


class InventoryRepository(Protocol):
    """Persistence contract for the Inventory aggregate root.

    Query methods return `Sequence[Inventory]` to ensure callers treat results
    as read-only data.
    """

    def add(self, inventory: Inventory) -> None:
        """Persist a newly initialized inventory projection."""
        ...

    def save(self, inventory: Inventory) -> None:
        """Persist changes to an existing inventory projection.

        Implementations use `Inventory.version` for optimistic-concurrency control.
        """
        ...

    def get_by_id(self, inventory_id: InventoryId) -> Inventory | None:
        """Retrieve inventory projection by its primary ID."""
        ...

    def get_by_batch_id(self, batch_id: MedicineBatchId) -> Inventory | None:
        """Retrieve inventory projection for a specific medicine batch."""
        ...

    def list_by_medicine_id(self, medicine_id: MedicineId) -> Sequence[Inventory]:
        """All inventory projections belonging to a medicine product."""
        ...

    def list_by_status(
        self, status: StockStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Inventory]:
        """List inventory projections matching a specific stock status."""
        ...

    def list_low_stock(self, *, offset: int = 0, limit: int = 50) -> Sequence[Inventory]:
        """List inventory items where available quantity is at or below reorder level."""
        ...

    def list_out_of_stock(self, *, offset: int = 0, limit: int = 50) -> Sequence[Inventory]:
        """List inventory items where available quantity is zero."""
        ...

    def list_overstocked(self, *, offset: int = 0, limit: int = 50) -> Sequence[Inventory]:
        """List inventory items where available quantity exceeds overstock level."""
        ...

    def count_by_status(self, status: StockStatus) -> int:
        """Count inventory projections in a given status."""
        ...

    def exists(self, inventory_id: InventoryId) -> bool:
        """Check if an inventory projection exists by ID."""
        ...

    def exists_for_batch(self, batch_id: MedicineBatchId) -> bool:
        """Check if an inventory projection already exists for a batch."""
        ...


class StockMovementRepository(Protocol):
    """Persistence contract for the immutable StockMovement ledger."""

    def add(self, movement: StockMovement) -> None:
        """Persist an immutable stock ledger entry."""
        ...

    def get_by_id(self, movement_id: StockMovementId) -> StockMovement | None:
        """Retrieve a stock movement entry by ID."""
        ...

    def list_by_inventory_id(
        self, inventory_id: InventoryId, *, offset: int = 0, limit: int = 100
    ) -> Sequence[StockMovement]:
        """Retrieve historical ledger movements for an inventory projection."""
        ...

    def list_by_batch_id(
        self, batch_id: MedicineBatchId, *, offset: int = 0, limit: int = 100
    ) -> Sequence[StockMovement]:
        """Retrieve historical ledger movements for a medicine batch."""
        ...

    def list_by_medicine_id(
        self, medicine_id: MedicineId, *, offset: int = 0, limit: int = 100
    ) -> Sequence[StockMovement]:
        """Retrieve historical ledger movements for a medicine product."""
        ...

    def list_by_source_document(
        self, document_id: UUID
    ) -> Sequence[StockMovement]:
        """Retrieve ledger entries originating from a specific commercial document."""
        ...
