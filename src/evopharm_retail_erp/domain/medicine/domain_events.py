"""
Domain Events for the Medicine bounded context in EvoPharm Retail ERP.

Domain events capture immutable historical facts regarding state changes within
the Medicine aggregate boundary in accordance with Domain-Driven Design (DDD).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True, kw_only=True)
class MedicineDomainEvent:
    """
    Base class for all domain events emitted by the Medicine aggregate.

    Attributes:
        medicine_id: Unique identifier of the Medicine aggregate root.
        event_id: Unique identifier for this event instance.
        occurred_at: UTC timestamp recording when the event took place.
    """

    medicine_id: UUID
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True, kw_only=True)
class MedicineRegistered(MedicineDomainEvent):
    """Emitted when a new Medicine aggregate is registered in the system."""

    name: str
    code: str
    category: str
    requires_prescription: bool
    is_controlled: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class MedicineUpdated(MedicineDomainEvent):
    """Emitted when core business attributes of a Medicine aggregate are updated."""

    name: str
    code: str
    category: str


@dataclass(frozen=True, slots=True, kw_only=True)
class MedicineDiscontinued(MedicineDomainEvent):
    """Emitted when a Medicine product line is discontinued."""

    reason: str


@dataclass(frozen=True, slots=True, kw_only=True)
class MedicineReactivated(MedicineDomainEvent):
    """Emitted when a previously discontinued Medicine is reactivated."""

    reason: str


@dataclass(frozen=True, slots=True, kw_only=True)
class MedicineBarcodeAdded(MedicineDomainEvent):
    """Emitted when a new barcode is associated with a Medicine aggregate."""

    barcode: str


@dataclass(frozen=True, slots=True, kw_only=True)
class MedicineAlternateNameAdded(MedicineDomainEvent):
    """Emitted when an alternate or generic alias is attached to a Medicine aggregate."""

    alternate_name: str