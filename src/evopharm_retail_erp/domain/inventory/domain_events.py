"""Domain events for the Inventory bounded context.

These represent completed immutable business facts occurring in the inventory domain.
None of them carry any dispatching or event bus dependency.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from ..medicine.value_objects import MedicineBatchId, MedicineId
from .value_objects import InventoryId, Quantity, StockMovementId


@dataclass(frozen=True, slots=True, kw_only=True)
class InventoryDomainEvent:
    """Base class for all domain events emitted by the Inventory domain."""

    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class InventoryCreated(InventoryDomainEvent):
    """Emitted when a new inventory projection is registered for a batch."""

    inventory_id: InventoryId
    medicine_id: MedicineId
    medicine_batch_id: MedicineBatchId
    initial_quantity: Quantity


@dataclass(frozen=True, slots=True, kw_only=True)
class StockReceived(InventoryDomainEvent):
    """Emitted when physical stock is received and added to on-hand inventory."""

    inventory_id: InventoryId
    medicine_id: MedicineId
    medicine_batch_id: MedicineBatchId
    movement_id: StockMovementId
    quantity_received: Quantity
    new_quantity_on_hand: Quantity


@dataclass(frozen=True, slots=True, kw_only=True)
class StockDispensed(InventoryDomainEvent):
    """Emitted when stock is dispensed for a customer sale."""

    inventory_id: InventoryId
    medicine_id: MedicineId
    medicine_batch_id: MedicineBatchId
    movement_id: StockMovementId
    quantity_dispensed: Quantity
    new_quantity_on_hand: Quantity


@dataclass(frozen=True, slots=True, kw_only=True)
class StockReserved(InventoryDomainEvent):
    """Emitted when stock is held in reservation."""

    inventory_id: InventoryId
    medicine_id: MedicineId
    medicine_batch_id: MedicineBatchId
    quantity_reserved: Quantity
    new_total_reserved: Quantity


@dataclass(frozen=True, slots=True, kw_only=True)
class StockReservationReleased(InventoryDomainEvent):
    """Emitted when reserved stock is released back to available pool."""

    inventory_id: InventoryId
    medicine_id: MedicineId
    medicine_batch_id: MedicineBatchId
    quantity_released: Quantity
    new_total_reserved: Quantity


@dataclass(frozen=True, slots=True, kw_only=True)
class StockReleased(StockReservationReleased):
    """Emitted when reserved stock is released back to available pool."""


@dataclass(frozen=True, slots=True, kw_only=True)
class StockAdjusted(InventoryDomainEvent):
    """Emitted when inventory is manually adjusted (count, damage, write-off)."""

    inventory_id: InventoryId
    medicine_id: MedicineId
    medicine_batch_id: MedicineBatchId
    movement_id: StockMovementId
    quantity_delta: int
    new_quantity_on_hand: Quantity
    reason: str


@dataclass(frozen=True, slots=True, kw_only=True)
class StockTransferred(InventoryDomainEvent):
    """Emitted when stock is transferred between locations or internal accounts."""

    inventory_id: InventoryId
    medicine_id: MedicineId
    medicine_batch_id: MedicineBatchId
    movement_id: StockMovementId
    quantity_transferred: Quantity
    destination_reference: str


@dataclass(frozen=True, slots=True, kw_only=True)
class StockWrittenOff(InventoryDomainEvent):
    """Emitted when expired or damaged stock is written off."""

    inventory_id: InventoryId
    medicine_id: MedicineId
    medicine_batch_id: MedicineBatchId
    movement_id: StockMovementId
    quantity_written_off: Quantity
    reason: str


@dataclass(frozen=True, slots=True, kw_only=True)
class LowStockAlertTriggered(InventoryDomainEvent):
    """Emitted when available stock drops to or below reorder level."""

    inventory_id: InventoryId
    medicine_id: MedicineId
    medicine_batch_id: MedicineBatchId
    quantity_available: Quantity
    reorder_level: Quantity


@dataclass(frozen=True, slots=True, kw_only=True)
class ReorderTriggered(LowStockAlertTriggered):
    """Emitted when inventory level drops to or below reorder threshold."""


@dataclass(frozen=True, slots=True, kw_only=True)
class OutOfStockAlertTriggered(InventoryDomainEvent):
    """Emitted when available stock reaches zero."""

    inventory_id: InventoryId
    medicine_id: MedicineId
    medicine_batch_id: MedicineBatchId
