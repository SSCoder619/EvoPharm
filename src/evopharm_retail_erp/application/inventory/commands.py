"""Command DTOs for the Inventory application use cases.

Commands are strongly typed, immutable input data transfer objects sent into application service handlers.
They contain no domain logic and have zero dependencies on ORM or web frameworks.
"""
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ReceiveStockCommand:
    """Command to record received physical stock for a medicine batch."""

    medicine_id: UUID
    medicine_batch_id: UUID
    quantity: int
    inventory_id: UUID | None = None
    document_type: str | None = None
    document_id: UUID | None = None
    reference_number: str | None = None
    reason: str | None = None
    performed_by_user_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class ReserveStockCommand:
    """Command to hold stock in reserved state prior to billing completion."""

    inventory_id: UUID
    quantity: int


@dataclass(frozen=True, slots=True)
class ReleaseStockCommand:
    """Command to release previously reserved stock back to available pool."""

    inventory_id: UUID
    quantity: int


@dataclass(frozen=True, slots=True)
class DispenseStockCommand:
    """Command to dispense stock for a retail sale."""

    inventory_id: UUID
    quantity: int
    document_type: str | None = None
    document_id: UUID | None = None
    reference_number: str | None = None
    reason: str | None = None
    performed_by_user_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class AdjustStockCommand:
    """Command to manually adjust stock levels for audit counts, damage, or expiry."""

    inventory_id: UUID
    quantity_delta: int
    reason: str
    document_type: str | None = None
    document_id: UUID | None = None
    reference_number: str | None = None
    performed_by_user_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class TransferStockCommand:
    """Command to transfer stock between two inventory locations."""

    from_inventory_id: UUID
    to_inventory_id: UUID
    quantity: int
    reason: str
    performed_by_user_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class WriteOffStockCommand:
    """Command to write off stock due to damage, theft, or expiry."""

    inventory_id: UUID
    quantity: int
    reason: str
    performed_by_user_id: UUID | None = None
