"""Domain exceptions for the Inventory bounded context.

Every exception here is raised from inside an aggregate, entity, or value object to
protect business invariants. None of them carry any dependency on infrastructure
or presentation concerns (no HTTP status codes, no ORM error wrapping) — translating
a domain error into a UI message or an API response is a job for an outer layer.
"""
from __future__ import annotations

from uuid import UUID


class InventoryDomainError(Exception):
    """Base class for every error raised by the Inventory domain."""


class InvalidQuantityError(InventoryDomainError):
    """Raised when a quantity value violates domain constraints."""

    def __init__(self, value: object, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid quantity {value!r}: {reason}")


class InvalidStockThresholdsError(InventoryDomainError):
    """Raised when inventory threshold configuration is invalid."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid stock thresholds: {reason}")


class InvalidSourceDocumentRefError(InventoryDomainError):
    """Raised when a source document reference is malformed."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid source document reference: {reason}")


class InvalidMovementReasonError(InventoryDomainError):
    """Raised when a stock movement reason description is invalid."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid movement reason: {reason}")


class InsufficientStockError(InventoryDomainError):
    """Raised when requested quantity exceeds available inventory."""

    def __init__(
        self,
        inventory_id: UUID,
        requested: int,
        available: int,
    ) -> None:
        self.inventory_id = inventory_id
        self.requested = requested
        self.available = available
        super().__init__(
            f"Insufficient stock for inventory {inventory_id}: requested {requested}, "
            f"available {available}"
        )


class NegativeStockError(InventoryDomainError):
    """Raised when an operation would cause stock on hand to drop below zero."""

    def __init__(
        self,
        inventory_id: UUID,
        current_on_hand: int,
        deduction: int,
    ) -> None:
        self.inventory_id = inventory_id
        self.current_on_hand = current_on_hand
        self.deduction = deduction
        super().__init__(
            f"Cannot deduct {deduction} from inventory {inventory_id}: current on hand is "
            f"{current_on_hand}"
        )


class InvalidStockReservationError(InventoryDomainError):
    """Raised when stock reservation or release violates business rules."""

    def __init__(self, inventory_id: UUID, reason: str) -> None:
        self.inventory_id = inventory_id
        self.reason = reason
        super().__init__(
            f"Invalid stock reservation operation for inventory {inventory_id}: {reason}"
        )


class InventoryItemNotFoundError(InventoryDomainError):
    """Raised when an inventory projection cannot be found."""

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier
        super().__init__(f"Inventory item not found: {identifier}")


class StockMovementNotFoundError(InventoryDomainError):
    """Raised when a stock movement ledger entry cannot be found."""

    def __init__(self, movement_id: UUID) -> None:
        self.movement_id = movement_id
        super().__init__(f"Stock movement not found: {movement_id}")


class InventoryAlreadyExistsError(InventoryDomainError):
    """Raised when trying to register duplicate inventory projection for a batch."""

    def __init__(self, batch_id: UUID) -> None:
        self.batch_id = batch_id
        super().__init__(
            f"Inventory projection already exists for batch {batch_id}"
        )


class InvalidMovementError(InventoryDomainError):
    """Raised when a stock movement operation violates domain rules."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid movement operation: {reason}")


class InvalidInventoryStateError(InventoryDomainError):
    """Raised when an inventory projection is in an invalid state for an operation."""

    def __init__(self, inventory_id: UUID, current_state: str, action: str) -> None:
        self.inventory_id = inventory_id
        self.current_state = current_state
        self.action = action
        super().__init__(
            f"Cannot perform {action} on inventory {inventory_id}: current state is {current_state}"
        )

