"""Domain events for the Sales bounded context.

These represent completed immutable historical facts occurring within the Sales aggregate boundary.
None of them carry any dispatching or event bus dependency.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from ..medicine.value_objects import MedicineBatchId, MedicineId
from .value_objects import (
    CustomerReference,
    InvoiceNumber,
    Money,
    PaymentReference,
    PrescriptionReference,
    SaleId,
    SaleLineId,
    SaleQuantity,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class SalesDomainEvent:
    """Base class for all domain events emitted by the Sale aggregate."""

    sale_id: SaleId
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class SaleCreated(SalesDomainEvent):
    """Emitted when a new retail sale aggregate is initialized."""

    customer_reference: CustomerReference
    invoice_number: InvoiceNumber


@dataclass(frozen=True, slots=True, kw_only=True)
class SaleLineAdded(SalesDomainEvent):
    """Emitted when a sale line item is added to a draft sale."""

    line_id: SaleLineId
    medicine_id: MedicineId
    batch_id: MedicineBatchId | None
    quantity: SaleQuantity
    unit_price: Money


@dataclass(frozen=True, slots=True, kw_only=True)
class SaleLineRemoved(SalesDomainEvent):
    """Emitted when a line item is removed from a draft sale."""

    line_id: SaleLineId
    medicine_id: MedicineId


@dataclass(frozen=True, slots=True, kw_only=True)
class PrescriptionAttached(SalesDomainEvent):
    """Emitted when a medical practitioner prescription reference is attached to a sale."""

    prescription_reference: PrescriptionReference


@dataclass(frozen=True, slots=True, kw_only=True)
class SaleConfirmed(SalesDomainEvent):
    """Emitted when a retail sale is confirmed for stock dispensing and billing."""

    total_amount: Money


@dataclass(frozen=True, slots=True, kw_only=True)
class SalePaymentRecorded(SalesDomainEvent):
    """Emitted when a payment transaction is recorded against a sale."""

    amount_paid: Money
    payment_method: str
    payment_status: str
    payment_reference: PaymentReference | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class SaleCompleted(SalesDomainEvent):
    """Emitted when a sale is fully settled and completed."""

    invoice_number: InvoiceNumber


@dataclass(frozen=True, slots=True, kw_only=True)
class SaleCancelled(SalesDomainEvent):
    """Emitted when a sale is cancelled."""

    reason: str


@dataclass(frozen=True, slots=True, kw_only=True)
class SaleReturned(SalesDomainEvent):
    """Emitted when physical units are returned by customer against a completed sale line."""

    line_id: SaleLineId
    medicine_id: MedicineId
    batch_id: MedicineBatchId | None
    returned_quantity: SaleQuantity
    return_reason: str
    refund_amount: Money
