"""Command DTOs for the Customer application use cases.

Commands are strongly typed, immutable input data transfer objects sent into application service handlers.
They contain no domain logic and have zero dependencies on ORM or web frameworks.
"""
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RegisterCustomerCommand:
    """Command to register a new retail customer profile."""

    name: str
    phone: str
    code: str | None = None
    email: str | None = None
    street: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    customer_type: str = "REGULAR"
    customer_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class UpdateCustomerContactCommand:
    """Command to update customer contact details (phone & email)."""

    customer_id: UUID
    phone: str
    email: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateCustomerAddressCommand:
    """Command to update customer delivery address."""

    customer_id: UUID
    street: str
    city: str
    state: str
    pincode: str


@dataclass(frozen=True, slots=True)
class UpdateCustomerProfileCommand:
    """Command to update customer name and type classification."""

    customer_id: UUID
    name: str
    customer_type: str = "REGULAR"


@dataclass(frozen=True, slots=True)
class ActivateCustomerCommand:
    """Command to activate a customer account."""

    customer_id: UUID
    reason: str = "Activated by operator"


@dataclass(frozen=True, slots=True)
class DeactivateCustomerCommand:
    """Command to deactivate a customer account."""

    customer_id: UUID
    reason: str


@dataclass(frozen=True, slots=True)
class SuspendCustomerCommand:
    """Command to suspend a customer account."""

    customer_id: UUID
    reason: str
