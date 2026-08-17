"""Result DTOs for the Inventory application use cases.

Read-only Data Transfer Objects returned by application service handlers to represent
the state of Inventory aggregates and StockMovement ledger entries without exposing domain entities or ORM instances.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from ...domain.inventory import Inventory, StockMovement


@dataclass(frozen=True, slots=True)
class StockMovementResult:
    """Read-only result DTO representing a stock movement ledger entry."""

    id: UUID
    inventory_id: UUID
    medicine_id: UUID
    medicine_batch_id: UUID
    movement_type: str
    direction: str
    quantity: int
    signed_delta: int
    reason: str | None
    performed_by_user_id: UUID | None
    occurred_at: datetime

    @classmethod
    def from_domain(cls, movement: StockMovement) -> StockMovementResult:
        """Map a StockMovement entity into an immutable StockMovementResult DTO."""
        return cls(
            id=movement.id.value,
            inventory_id=movement.inventory_id.value,
            medicine_id=movement.medicine_id.value,
            medicine_batch_id=movement.medicine_batch_id.value,
            movement_type=movement.movement_type.value,
            direction=movement.direction.value,
            quantity=movement.quantity.value,
            signed_delta=movement.signed_quantity_delta,
            reason=movement.reason.description if movement.reason else None,
            performed_by_user_id=movement.performed_by_user_id,
            occurred_at=movement.occurred_at,
        )


@dataclass(frozen=True, slots=True)
class InventoryResult:
    """Read-only result DTO representing a complete Inventory aggregate projection."""

    inventory_id: UUID
    medicine_id: UUID
    medicine_batch_id: UUID
    quantity_on_hand: int
    quantity_reserved: int
    quantity_available: int
    status: str
    version: int
    last_movement_at: datetime
    created_at: datetime
    updated_at: datetime
    movements: tuple[StockMovementResult, ...]

    @classmethod
    def from_domain(cls, inventory: Inventory) -> InventoryResult:
        """Map an Inventory aggregate root into an immutable InventoryResult DTO."""
        return cls(
            inventory_id=inventory.id.value,
            medicine_id=inventory.medicine_id.value,
            medicine_batch_id=inventory.medicine_batch_id.value,
            quantity_on_hand=inventory.quantity_on_hand.value,
            quantity_reserved=inventory.quantity_reserved.value,
            quantity_available=inventory.quantity_available.value,
            status=inventory.status.value,
            version=inventory.version,
            last_movement_at=inventory.last_movement_at,
            created_at=inventory.created_at,
            updated_at=inventory.updated_at,
            movements=tuple(StockMovementResult.from_domain(m) for m in inventory.movements),
        )
