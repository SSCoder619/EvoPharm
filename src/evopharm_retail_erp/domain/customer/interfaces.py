"""Repository interfaces (ports) for the Customer domain.

These are pure contracts — no implementation, no ORM, no SQL. They define what
the Customer domain requires from persistence; concrete adapters (SQL, in-memory, etc.)
live in the Infrastructure layer and satisfy these Protocols structurally.
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, TYPE_CHECKING

from .enums import CustomerStatus
from .value_objects import (
    CustomerCode,
    CustomerId,
    PhoneNumber,
)

if TYPE_CHECKING:
    from .entities import Customer


class CustomerRepository(Protocol):
    """Persistence contract for the Customer aggregate root.

    Query methods return `Sequence[Customer]` to ensure callers treat results
    as read-only data.
    """

    def add(self, customer: Customer) -> None:
        """Persist a newly registered retail customer aggregate."""
        ...

    def save(self, customer: Customer) -> None:
        """Persist modifications to an existing customer aggregate.

        Implementations are expected to use `Customer.version` for
        optimistic-concurrency control.
        """
        ...

    def get_by_id(self, customer_id: CustomerId) -> Customer | None:
        """Retrieve a customer aggregate by its primary ID."""
        ...

    def get_by_code(self, code: CustomerCode) -> Customer | None:
        """Retrieve a customer aggregate by unique customer code."""
        ...

    def get_by_phone(self, phone: PhoneNumber) -> Customer | None:
        """Retrieve a customer aggregate matching a primary contact phone number."""
        ...

    def list_by_status(
        self, status: CustomerStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Customer]:
        """List customer aggregates matching a specific status."""
        ...

    def count_by_status(self, status: CustomerStatus) -> int:
        """Count total customer records in a given status."""
        ...

    def exists(self, customer_id: CustomerId) -> bool:
        """Check if a customer exists by ID."""
        ...

    def exists_code(self, code: CustomerCode) -> bool:
        """Check if a customer code is already registered."""
        ...
