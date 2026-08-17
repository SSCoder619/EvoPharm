"""Entities for the Supplier bounded context.

Following DDD principles, Supplier is the Aggregate Root representing a pharmaceutical
supplier / vendor and managing identity, compliance credentials (GSTIN/PAN), and status lifecycle.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from .domain_events import (
    SupplierActivated,
    SupplierAddressUpdated,
    SupplierArchived,
    SupplierComplianceUpdated,
    SupplierContactUpdated,
    SupplierDeactivated,
    SupplierDetailsUpdated,
    SupplierDomainEvent,
    SupplierReactivated,
    SupplierRegistered,
    SupplierSuspended,
)
from .enums import SupplierCategory, SupplierStatus
from .exceptions import (
    InvalidSupplierStateError,
    SupplierAlreadyActiveError,
    SupplierAlreadyInactiveError,
)
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


@dataclass(slots=True, eq=False)
class Supplier:
    """Aggregate Root representing a pharmaceutical supplier/vendor profile."""

    id: SupplierId
    code: SupplierCode
    name: SupplierName
    phone: PhoneNumber
    email: EmailAddress | None = None
    address: Address | None = None
    gstin: GSTIN | None = None
    pan: PAN | None = None
    status: SupplierStatus = SupplierStatus.ACTIVE
    category: SupplierCategory = SupplierCategory.DISTRIBUTOR
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1
    _events: list[SupplierDomainEvent] = field(default_factory=list)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Supplier):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    # -- Factory --------------------------------------------------------

    @classmethod
    def register(
        cls,
        name: SupplierName,
        phone: PhoneNumber,
        code: SupplierCode | None = None,
        email: EmailAddress | None = None,
        address: Address | None = None,
        gstin: GSTIN | None = None,
        pan: PAN | None = None,
        category: SupplierCategory = SupplierCategory.DISTRIBUTOR,
        id: SupplierId | None = None,
    ) -> "Supplier":
        """Register a new pharmaceutical supplier aggregate root."""
        s_id = id if id is not None else SupplierId.generate()
        s_code = code if code is not None else SupplierCode(f"SUP-{s_id.value.hex[:8].upper()}")
        now = datetime.now(timezone.utc)

        supplier = cls(
            id=s_id,
            code=s_code,
            name=name,
            phone=phone,
            email=email,
            address=address,
            gstin=gstin,
            pan=pan,
            status=SupplierStatus.ACTIVE,
            category=category,
            created_at=now,
            updated_at=now,
        )
        supplier._record_event(
            SupplierRegistered(
                supplier_id=s_id,
                code=s_code,
                name=name,
                phone=phone,
                email=email,
            )
        )
        return supplier

    # -- Properties & Domain Events -------------------------------------

    @property
    def is_active(self) -> bool:
        return self.status == SupplierStatus.ACTIVE

    @property
    def is_tax_compliant(self) -> bool:
        """Indicates if the supplier has registered valid GSTIN and PAN details."""
        return self.gstin is not None and self.pan is not None

    @property
    def events(self) -> tuple[SupplierDomainEvent, ...]:
        """Read-only tuple of uncommitted domain events emitted by this aggregate."""
        return tuple(self._events)

    def clear_events(self) -> None:
        """Clear all domain events after dispatch."""
        self._events.clear()

    # -- Internal Helpers -----------------------------------------------

    def _touch(self) -> None:
        """Update timestamp and increment optimistic concurrency version."""
        self.updated_at = datetime.now(timezone.utc)
        self.version += 1

    def _record_event(self, event: SupplierDomainEvent) -> None:
        self._events.append(event)

    # -- Lifecycle Operations -------------------------------------------

    def activate(self, reason: str = "Activated by procurement operator") -> None:
        """Activate an inactive supplier account."""
        if self.status == SupplierStatus.ACTIVE:
            raise SupplierAlreadyActiveError(self.id.value)
        if self.status == SupplierStatus.SUSPENDED:
            raise InvalidSupplierStateError(
                self.id.value, self.status.value, "Use reactivate() for suspended suppliers"
            )
        if self.status == SupplierStatus.ARCHIVED:
            raise InvalidSupplierStateError(
                self.id.value, self.status.value, SupplierStatus.ACTIVE.value
            )

        self.status = SupplierStatus.ACTIVE
        self._touch()
        self._record_event(
            SupplierActivated(
                supplier_id=self.id,
                reason=reason,
            )
        )

    def deactivate(self, reason: str) -> None:
        """Deactivate an active supplier account."""
        clean_reason = reason.strip()
        if not clean_reason:
            raise InvalidSupplierStateError(
                self.id.value, self.status.value, "DEACTIVATION_WITHOUT_REASON"
            )

        if self.status == SupplierStatus.INACTIVE:
            raise SupplierAlreadyInactiveError(self.id.value)
        if self.status == SupplierStatus.ARCHIVED:
            raise InvalidSupplierStateError(
                self.id.value, self.status.value, SupplierStatus.INACTIVE.value
            )

        self.status = SupplierStatus.INACTIVE
        self._touch()
        self._record_event(
            SupplierDeactivated(
                supplier_id=self.id,
                reason=clean_reason,
            )
        )

    def suspend(self, reason: str) -> None:
        """Suspend a supplier account due to quality or compliance holds."""
        clean_reason = reason.strip()
        if not clean_reason:
            raise InvalidSupplierStateError(
                self.id.value, self.status.value, "SUSPENSION_WITHOUT_REASON"
            )
        if self.status == SupplierStatus.ARCHIVED:
            raise InvalidSupplierStateError(
                self.id.value, self.status.value, SupplierStatus.SUSPENDED.value
            )

        self.status = SupplierStatus.SUSPENDED
        self._touch()
        self._record_event(
            SupplierSuspended(
                supplier_id=self.id,
                reason=clean_reason,
            )
        )

    def reactivate(self, reason: str = "Reactivated by compliance clearance") -> None:
        """Reactivate a suspended or inactive supplier account."""
        if self.status == SupplierStatus.ACTIVE:
            raise SupplierAlreadyActiveError(self.id.value)
        if self.status == SupplierStatus.ARCHIVED:
            raise InvalidSupplierStateError(
                self.id.value, self.status.value, SupplierStatus.ACTIVE.value
            )

        self.status = SupplierStatus.ACTIVE
        self._touch()
        self._record_event(
            SupplierReactivated(
                supplier_id=self.id,
                reason=reason,
            )
        )

    def archive(self, reason: str) -> None:
        """Archive a supplier account permanently."""
        clean_reason = reason.strip()
        if not clean_reason:
            raise InvalidSupplierStateError(
                self.id.value, self.status.value, "ARCHIVAL_WITHOUT_REASON"
            )

        self.status = SupplierStatus.ARCHIVED
        self._touch()
        self._record_event(
            SupplierArchived(
                supplier_id=self.id,
                reason=clean_reason,
            )
        )

    # -- Profile Updates ------------------------------------------------

    def update_contact_information(
        self,
        phone: PhoneNumber,
        email: EmailAddress | None = None,
    ) -> None:
        """Update supplier contact details (phone number and email)."""
        self.phone = phone
        self.email = email
        self._touch()
        self._record_event(
            SupplierContactUpdated(
                supplier_id=self.id,
                phone=phone,
                email=email,
            )
        )

    def update_address(self, address: Address) -> None:
        """Update supplier registered office address."""
        self.address = address
        self._touch()
        self._record_event(
            SupplierAddressUpdated(
                supplier_id=self.id,
                address=address,
            )
        )

    def update_compliance_information(
        self,
        gstin: GSTIN | None = None,
        pan: PAN | None = None,
    ) -> None:
        """Update supplier tax compliance identifiers (GSTIN / PAN)."""
        self.gstin = gstin
        self.pan = pan
        self._touch()
        self._record_event(
            SupplierComplianceUpdated(
                supplier_id=self.id,
                gstin=gstin,
                pan=pan,
            )
        )

    def update_supplier_details(
        self,
        name: SupplierName,
        category: SupplierCategory = SupplierCategory.DISTRIBUTOR,
    ) -> None:
        """Update supplier legal business name and category."""
        self.name = name
        self.category = category
        self._touch()
        self._record_event(
            SupplierDetailsUpdated(
                supplier_id=self.id,
                name=name,
                category=category.value,
            )
        )
