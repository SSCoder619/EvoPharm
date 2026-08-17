"""Command DTOs for the Supplier application use cases.

Commands are strongly typed, immutable input data transfer objects sent into application service handlers.
They contain no domain logic and have zero dependencies on ORM or web frameworks.
"""
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RegisterSupplierCommand:
    """Command to register a new pharmaceutical supplier profile."""

    name: str
    phone: str
    code: str | None = None
    email: str | None = None
    street: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    gstin: str | None = None
    pan: str | None = None
    category: str = "DISTRIBUTOR"
    supplier_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class UpdateSupplierContactCommand:
    """Command to update supplier contact details (phone & email)."""

    supplier_id: UUID
    phone: str
    email: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateSupplierAddressCommand:
    """Command to update supplier registered office address."""

    supplier_id: UUID
    street: str
    city: str
    state: str
    pincode: str


@dataclass(frozen=True, slots=True)
class UpdateSupplierComplianceCommand:
    """Command to update supplier tax compliance credentials (GSTIN / PAN)."""

    supplier_id: UUID
    gstin: str | None = None
    pan: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateSupplierDetailsCommand:
    """Command to update supplier legal business name and category."""

    supplier_id: UUID
    name: str
    category: str = "DISTRIBUTOR"


@dataclass(frozen=True, slots=True)
class ActivateSupplierCommand:
    """Command to activate an inactive supplier account."""

    supplier_id: UUID
    reason: str = "Activated by procurement operator"


@dataclass(frozen=True, slots=True)
class DeactivateSupplierCommand:
    """Command to deactivate an active supplier account."""

    supplier_id: UUID
    reason: str


@dataclass(frozen=True, slots=True)
class SuspendSupplierCommand:
    """Command to suspend a supplier account due to quality or compliance holds."""

    supplier_id: UUID
    reason: str


@dataclass(frozen=True, slots=True)
class ReactivateSupplierCommand:
    """Command to reactivate a suspended supplier account."""

    supplier_id: UUID
    reason: str = "Reactivated by compliance clearance"
