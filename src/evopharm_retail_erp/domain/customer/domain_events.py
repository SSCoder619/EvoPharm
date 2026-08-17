"""Domain events for the Customer bounded context.

These represent completed immutable historical facts occurring within the Customer aggregate boundary.
None of them carry any dispatching or event bus dependency.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from .value_objects import (
    Address,
    CustomerCode,
    CustomerId,
    CustomerName,
    EmailAddress,
    PhoneNumber,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class CustomerDomainEvent:
    """Base class for all domain events emitted by the Customer aggregate."""

    customer_id: CustomerId
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class CustomerRegistered(CustomerDomainEvent):
    """Emitted when a new customer aggregate is registered."""

    code: CustomerCode
    name: CustomerName
    phone: PhoneNumber
    email: EmailAddress | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class CustomerActivated(CustomerDomainEvent):
    """Emitted when a customer is activated."""

    reason: str = "Activated by operator"


@dataclass(frozen=True, slots=True, kw_only=True)
class CustomerDeactivated(CustomerDomainEvent):
    """Emitted when a customer is deactivated."""

    reason: str


@dataclass(frozen=True, slots=True, kw_only=True)
class CustomerSuspended(CustomerDomainEvent):
    """Emitted when a customer account is suspended."""

    reason: str


@dataclass(frozen=True, slots=True, kw_only=True)
class CustomerContactUpdated(CustomerDomainEvent):
    """Emitted when contact information (phone or email) is updated."""

    phone: PhoneNumber
    email: EmailAddress | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class CustomerAddressUpdated(CustomerDomainEvent):
    """Emitted when a customer's primary address is updated."""

    address: Address


@dataclass(frozen=True, slots=True, kw_only=True)
class CustomerProfileUpdated(CustomerDomainEvent):
    """Emitted when customer profile details (name or customer_type) are updated."""

    name: CustomerName
    customer_type: str
