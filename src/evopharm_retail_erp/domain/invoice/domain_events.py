"""Domain events for the Invoice bounded context.

These represent completed immutable historical facts occurring within the Invoice aggregate boundary.
None of them carry any dispatching or event bus dependency.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from ..medicine.value_objects import MedicineBatchId, MedicineId
from .value_objects import (
    CustomerReference,
    InvoiceId,
    InvoiceLineId,
    InvoiceNumber,
    InvoiceQuantity,
    Money,
    SaleReference,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class InvoiceDomainEvent:
    """Base class for all domain events emitted by the Invoice aggregate."""

    invoice_id: InvoiceId
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class InvoiceCreated(InvoiceDomainEvent):
    """Emitted when a new retail invoice aggregate is initialized."""

    number: InvoiceNumber
    sale_reference: SaleReference | None = None
    customer_reference: CustomerReference | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class InvoiceLineAdded(InvoiceDomainEvent):
    """Emitted when an item line is added to a draft invoice."""

    line_id: InvoiceLineId
    medicine_id: MedicineId
    batch_id: MedicineBatchId | None
    quantity: InvoiceQuantity
    unit_price: Money


@dataclass(frozen=True, slots=True, kw_only=True)
class InvoiceLineRemoved(InvoiceDomainEvent):
    """Emitted when an item line is removed from a draft invoice."""

    line_id: InvoiceLineId
    medicine_id: MedicineId


@dataclass(frozen=True, slots=True, kw_only=True)
class InvoiceIssued(InvoiceDomainEvent):
    """Emitted when an invoice is issued to the customer."""

    number: InvoiceNumber
    total_amount: Money


@dataclass(frozen=True, slots=True, kw_only=True)
class InvoicePaymentRecorded(InvoiceDomainEvent):
    """Emitted when a payment transaction is recorded against an invoice."""

    amount_paid: Money
    payment_status: str
    remaining_balance: Money


@dataclass(frozen=True, slots=True, kw_only=True)
class InvoicePaid(InvoiceDomainEvent):
    """Emitted when an invoice is fully paid."""

    number: InvoiceNumber
    total_amount: Money


@dataclass(frozen=True, slots=True, kw_only=True)
class InvoicePartiallyPaid(InvoiceDomainEvent):
    """Emitted when an invoice is partially paid."""

    amount_paid: Money
    remaining_balance: Money


@dataclass(frozen=True, slots=True, kw_only=True)
class InvoiceCancelled(InvoiceDomainEvent):
    """Emitted when an invoice is cancelled."""

    reason: str
