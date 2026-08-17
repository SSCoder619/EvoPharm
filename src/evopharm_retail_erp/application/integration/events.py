"""Application integration event envelopes and contracts.

Defines immutable integration message wrappers carrying domain facts across bounded-context
boundaries without tight coupling or broker infrastructure.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Generic, TypeVar
from uuid import UUID, uuid4

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class IntegrationEvent(Generic[T]):
    """Generic integration message envelope carrying domain facts across contexts."""

    event_id: UUID
    source_context: str
    event_type: str
    occurred_at: datetime
    payload: T

    @classmethod
    def create(
        cls,
        source_context: str,
        event_type: str,
        payload: T,
        event_id: UUID | None = None,
        occurred_at: datetime | None = None,
    ) -> IntegrationEvent[T]:
        """Factory method to construct an immutable IntegrationEvent envelope."""
        return cls(
            event_id=event_id if event_id is not None else uuid4(),
            source_context=source_context,
            event_type=event_type,
            occurred_at=occurred_at if occurred_at is not None else datetime.now(timezone.utc),
            payload=payload,
        )


@dataclass(frozen=True, slots=True)
class PurchaseReceivedPayload:
    """Integration payload representing received purchase stock."""

    purchase_id: UUID
    line_id: UUID
    medicine_id: UUID
    received_quantity: int
    batch_number: str
    batch_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class SaleCompletedPayload:
    """Integration payload representing a completed retail sale."""

    sale_id: UUID
    invoice_number: str
    customer_id: UUID | None = None
    customer_name: str | None = None


@dataclass(frozen=True, slots=True)
class SaleReturnedPayload:
    """Integration payload representing returned sale items."""

    sale_id: UUID
    line_id: UUID
    medicine_id: UUID
    returned_quantity: int
    return_reason: str
    batch_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class InvoicePaidPayload:
    """Integration payload representing a fully paid invoice."""

    invoice_id: UUID
    invoice_number: str
    total_amount: str
