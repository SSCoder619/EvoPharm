"""Domain events for the Purchase bounded context.

These represent completed immutable historical facts occurring within the Purchase aggregate boundary.
None of them carry any dispatching or event bus dependency.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from ..medicine.value_objects import MedicineId
from .value_objects import (
    InvoiceReference,
    Money,
    PurchaseId,
    PurchaseLineId,
    PurchaseOrderReference,
    PurchaseQuantity,
    SupplierReference,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PurchaseDomainEvent:
    """Base class for all domain events emitted by the Purchase aggregate."""

    purchase_id: PurchaseId
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class PurchaseCreated(PurchaseDomainEvent):
    """Emitted when a new purchase order aggregate is initialized."""

    supplier_reference: SupplierReference
    order_reference: PurchaseOrderReference


@dataclass(frozen=True, slots=True, kw_only=True)
class PurchaseLineAdded(PurchaseDomainEvent):
    """Emitted when a new purchase order line is added to a draft purchase."""

    line_id: PurchaseLineId
    medicine_id: MedicineId
    ordered_quantity: PurchaseQuantity
    unit_price: Money


@dataclass(frozen=True, slots=True, kw_only=True)
class PurchaseLineRemoved(PurchaseDomainEvent):
    """Emitted when a line item is removed from a draft purchase order."""

    line_id: PurchaseLineId
    medicine_id: MedicineId


@dataclass(frozen=True, slots=True, kw_only=True)
class PurchaseApproved(PurchaseDomainEvent):
    """Emitted when a purchase order is officially approved."""

    approved_by_user_id: UUID | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class PurchaseOrdered(PurchaseDomainEvent):
    """Emitted when an approved purchase order is transmitted/placed with the supplier."""

    supplier_reference: SupplierReference


@dataclass(frozen=True, slots=True, kw_only=True)
class PurchasePartiallyReceived(PurchaseDomainEvent):
    """Emitted when physical stock is partially received against a purchase order line."""

    line_id: PurchaseLineId
    medicine_id: MedicineId
    received_quantity: PurchaseQuantity
    batch_number: str
    remaining_quantity: PurchaseQuantity


@dataclass(frozen=True, slots=True, kw_only=True)
class PurchaseReceived(PurchaseDomainEvent):
    """Emitted when all ordered line quantities on a purchase order have been received."""

    total_items_received: int


@dataclass(frozen=True, slots=True, kw_only=True)
class PurchaseCancelled(PurchaseDomainEvent):
    """Emitted when a purchase order is cancelled."""

    reason: str


@dataclass(frozen=True, slots=True, kw_only=True)
class PurchasePaymentRecorded(PurchaseDomainEvent):
    """Emitted when a payment transaction is recorded against a purchase order."""

    amount_paid: Money
    payment_status: str


@dataclass(frozen=True, slots=True, kw_only=True)
class PurchaseInvoiceAttached(PurchaseDomainEvent):
    """Emitted when a commercial supplier invoice reference is attached to a purchase order."""

    invoice_reference: InvoiceReference
