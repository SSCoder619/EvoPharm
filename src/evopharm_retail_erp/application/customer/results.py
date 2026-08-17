"""Result DTOs for the Customer application use cases.

Read-only Data Transfer Objects returned by application service handlers to represent
the state of Customer aggregates without exposing domain entities or ORM instances.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from ...domain.customer import Address, Customer


@dataclass(frozen=True, slots=True)
class AddressResult:
    """Read-only result DTO representing a postal delivery address."""

    street: str
    city: str
    state: str
    pincode: str

    @classmethod
    def from_domain(cls, addr: Address) -> AddressResult:
        """Map an Address value object into a DTO."""
        return cls(
            street=addr.street,
            city=addr.city,
            state=addr.state,
            pincode=addr.postal_code.value,
        )


@dataclass(frozen=True, slots=True)
class CustomerResult:
    """Read-only result DTO representing a complete Customer aggregate."""

    customer_id: UUID
    code: str
    name: str
    phone: str
    email: str | None
    address: AddressResult | None
    status: str
    customer_type: str
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, customer: Customer) -> CustomerResult:
        """Map a Customer aggregate root into an immutable CustomerResult DTO."""
        return cls(
            customer_id=customer.id.value,
            code=customer.code.value,
            name=customer.name.value,
            phone=customer.phone.value,
            email=customer.email.value if customer.email else None,
            address=AddressResult.from_domain(customer.address) if customer.address else None,
            status=customer.status.value,
            customer_type=customer.customer_type.value,
            version=customer.version,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
        )
