"""Domain events for the Supplier bounded context.

These represent completed immutable historical facts occurring within the Supplier aggregate boundary.
None of them carry any dispatching or event bus dependency.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from .value_objects import (
    GSTIN,
    PAN,
    Address,
    EmailAddress,
    PhoneNumber,
    SupplierCode,
    SupplierId,
    SupplierName,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class SupplierDomainEvent:
    """Base class for all domain events emitted by the Supplier aggregate."""

    supplier_id: SupplierId
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class SupplierRegistered(SupplierDomainEvent):
    """Emitted when a new supplier aggregate is registered."""

    code: SupplierCode
    name: SupplierName
    phone: PhoneNumber
    email: EmailAddress | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class SupplierActivated(SupplierDomainEvent):
    """Emitted when a supplier is activated."""

    reason: str = "Activated by procurement operator"


@dataclass(frozen=True, slots=True, kw_only=True)
class SupplierDeactivated(SupplierDomainEvent):
    """Emitted when a supplier is deactivated."""

    reason: str


@dataclass(frozen=True, slots=True, kw_only=True)
class SupplierSuspended(SupplierDomainEvent):
    """Emitted when a supplier account is suspended."""

    reason: str


@dataclass(frozen=True, slots=True, kw_only=True)
class SupplierReactivated(SupplierDomainEvent):
    """Emitted when a suspended or inactive supplier account is reactivated."""

    reason: str


@dataclass(frozen=True, slots=True, kw_only=True)
class SupplierArchived(SupplierDomainEvent):
    """Emitted when a supplier account is archived."""

    reason: str


@dataclass(frozen=True, slots=True, kw_only=True)
class SupplierContactUpdated(SupplierDomainEvent):
    """Emitted when contact information (phone or email) is updated."""

    phone: PhoneNumber
    email: EmailAddress | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class SupplierAddressUpdated(SupplierDomainEvent):
    """Emitted when a supplier's office address is updated."""

    address: Address


@dataclass(frozen=True, slots=True, kw_only=True)
class SupplierComplianceUpdated(SupplierDomainEvent):
    """Emitted when supplier tax compliance identifiers (GSTIN / PAN) are updated."""

    gstin: GSTIN | None = None
    pan: PAN | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class SupplierDetailsUpdated(SupplierDomainEvent):
    """Emitted when supplier details (name or category) are updated."""

    name: SupplierName
    category: str
