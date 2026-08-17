"""Entities for the Customer bounded context.

Following DDD principles, Customer is the Aggregate Root representing a retail
pharmacy customer and managing their identity, contact profile, and status lifecycle.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from .domain_events import (
    CustomerActivated,
    CustomerAddressUpdated,
    CustomerContactUpdated,
    CustomerDeactivated,
    CustomerDomainEvent,
    CustomerProfileUpdated,
    CustomerRegistered,
    CustomerSuspended,
)
from .enums import CustomerStatus, CustomerType
from .exceptions import (
    CustomerAlreadyActiveError,
    CustomerAlreadyInactiveError,
    InvalidCustomerStateError,
)
from .value_objects import (
    Address,
    CustomerCode,
    CustomerId,
    CustomerName,
    EmailAddress,
    PhoneNumber,
)


@dataclass(slots=True, eq=False)
class Customer:
    """Aggregate Root representing a retail pharmacy customer profile."""

    id: CustomerId
    code: CustomerCode
    name: CustomerName
    phone: PhoneNumber
    email: EmailAddress | None = None
    address: Address | None = None
    status: CustomerStatus = CustomerStatus.ACTIVE
    customer_type: CustomerType = CustomerType.REGULAR
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1
    _events: list[CustomerDomainEvent] = field(default_factory=list)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Customer):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    # -- Factory --------------------------------------------------------

    @classmethod
    def register(
        cls,
        name: CustomerName,
        phone: PhoneNumber,
        code: CustomerCode | None = None,
        email: EmailAddress | None = None,
        address: Address | None = None,
        customer_type: CustomerType = CustomerType.REGULAR,
        id: CustomerId | None = None,
    ) -> "Customer":
        """Register a new customer profile."""
        c_id = id if id is not None else CustomerId.generate()
        c_code = code if code is not None else CustomerCode(f"CUST-{c_id.value.hex[:8].upper()}")
        now = datetime.now(timezone.utc)

        customer = cls(
            id=c_id,
            code=c_code,
            name=name,
            phone=phone,
            email=email,
            address=address,
            status=CustomerStatus.ACTIVE,
            customer_type=customer_type,
            created_at=now,
            updated_at=now,
        )
        customer._record_event(
            CustomerRegistered(
                customer_id=c_id,
                code=c_code,
                name=name,
                phone=phone,
                email=email,
            )
        )
        return customer

    # -- Properties & Domain Events -------------------------------------

    @property
    def is_active(self) -> bool:
        return self.status == CustomerStatus.ACTIVE

    @property
    def events(self) -> tuple[CustomerDomainEvent, ...]:
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

    def _record_event(self, event: CustomerDomainEvent) -> None:
        self._events.append(event)

    # -- Lifecycle Operations -------------------------------------------

    def activate(self, reason: str = "Activated by operator") -> None:
        """Activate an inactive or suspended customer account."""
        if self.status == CustomerStatus.ACTIVE:
            raise CustomerAlreadyActiveError(self.id.value)
        if self.status == CustomerStatus.ARCHIVED:
            raise InvalidCustomerStateError(
                self.id.value, self.status.value, CustomerStatus.ACTIVE.value
            )

        self.status = CustomerStatus.ACTIVE
        self._touch()
        self._record_event(
            CustomerActivated(
                customer_id=self.id,
                reason=reason,
            )
        )

    def deactivate(self, reason: str) -> None:
        """Deactivate an active customer account."""
        clean_reason = reason.strip()
        if not clean_reason:
            raise InvalidCustomerStateError(
                self.id.value, self.status.value, "DEACTIVATION_WITHOUT_REASON"
            )

        if self.status == CustomerStatus.INACTIVE:
            raise CustomerAlreadyInactiveError(self.id.value)
        if self.status == CustomerStatus.ARCHIVED:
            raise InvalidCustomerStateError(
                self.id.value, self.status.value, CustomerStatus.INACTIVE.value
            )

        self.status = CustomerStatus.INACTIVE
        self._touch()
        self._record_event(
            CustomerDeactivated(
                customer_id=self.id,
                reason=clean_reason,
            )
        )

    def suspend(self, reason: str) -> None:
        """Suspend a customer account due to compliance or billing issues."""
        clean_reason = reason.strip()
        if not clean_reason:
            raise InvalidCustomerStateError(
                self.id.value, self.status.value, "SUSPENSION_WITHOUT_REASON"
            )

        if self.status == CustomerStatus.ARCHIVED:
            raise InvalidCustomerStateError(
                self.id.value, self.status.value, CustomerStatus.SUSPENDED.value
            )

        self.status = CustomerStatus.SUSPENDED
        self._touch()
        self._record_event(
            CustomerSuspended(
                customer_id=self.id,
                reason=clean_reason,
            )
        )

    # -- Profile Updates ------------------------------------------------

    def update_contact_information(
        self,
        phone: PhoneNumber,
        email: EmailAddress | None = None,
    ) -> None:
        """Update customer contact details (phone number and email)."""
        self.phone = phone
        self.email = email
        self._touch()
        self._record_event(
            CustomerContactUpdated(
                customer_id=self.id,
                phone=phone,
                email=email,
            )
        )

    def update_address(self, address: Address) -> None:
        """Update customer delivery address."""
        self.address = address
        self._touch()
        self._record_event(
            CustomerAddressUpdated(
                customer_id=self.id,
                address=address,
            )
        )

    def update_profile(
        self,
        name: CustomerName,
        customer_type: CustomerType = CustomerType.REGULAR,
    ) -> None:
        """Update customer name and type classification."""
        self.name = name
        self.customer_type = customer_type
        self._touch()
        self._record_event(
            CustomerProfileUpdated(
                customer_id=self.id,
                name=name,
                customer_type=customer_type.value,
            )
        )
