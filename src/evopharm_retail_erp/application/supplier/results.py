"""Result DTOs for the Supplier application use cases.

Read-only Data Transfer Objects returned by application service handlers to represent
the state of Supplier aggregates without exposing domain entities or ORM instances.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from ...domain.supplier import Address, Supplier


@dataclass(frozen=True, slots=True)
class AddressResult:
    """Read-only result DTO representing a registered office address."""

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
class SupplierResult:
    """Read-only result DTO representing a complete Supplier aggregate."""

    supplier_id: UUID
    code: str
    name: str
    phone: str
    email: str | None
    address: AddressResult | None
    gstin: str | None
    pan: str | None
    status: str
    category: str
    is_tax_compliant: bool
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, supplier: Supplier) -> SupplierResult:
        """Map a Supplier aggregate root into an immutable SupplierResult DTO."""
        return cls(
            supplier_id=supplier.id.value,
            code=supplier.code.value,
            name=supplier.name.value,
            phone=supplier.phone.value,
            email=supplier.email.value if supplier.email else None,
            address=AddressResult.from_domain(supplier.address) if supplier.address else None,
            gstin=supplier.gstin.value if supplier.gstin else None,
            pan=supplier.pan.value if supplier.pan else None,
            status=supplier.status.value,
            category=supplier.category.value,
            is_tax_compliant=supplier.is_tax_compliant,
            version=supplier.version,
            created_at=supplier.created_at,
            updated_at=supplier.updated_at,
        )
