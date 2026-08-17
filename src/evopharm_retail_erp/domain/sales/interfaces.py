"""Repository interfaces (ports) for the Sales domain.

These are pure contracts — no implementation, no ORM, no SQL. They define what
the Sales domain requires from persistence; concrete adapters (SQL, in-memory, etc.)
live in the Infrastructure layer and satisfy these Protocols structurally.
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, TYPE_CHECKING

from .enums import SaleStatus
from .value_objects import (
    CustomerReference,
    InvoiceNumber,
    SaleId,
)

if TYPE_CHECKING:
    from .entities import Sale


class SaleRepository(Protocol):
    """Persistence contract for the Sale aggregate root.

    Query methods return `Sequence[Sale]` to ensure callers treat results
    as read-only data.
    """

    def add(self, sale: Sale) -> None:
        """Persist a newly created retail sale aggregate."""
        ...

    def save(self, sale: Sale) -> None:
        """Persist modifications to an existing retail sale aggregate.

        Implementations are expected to use `Sale.version` for
        optimistic-concurrency control.
        """
        ...

    def get_by_id(self, sale_id: SaleId) -> Sale | None:
        """Retrieve a retail sale aggregate by its primary ID."""
        ...

    def get_by_invoice_number(
        self, invoice_number: InvoiceNumber
    ) -> Sale | None:
        """Retrieve a retail sale matching a unique invoice document number."""
        ...

    def list_by_customer(
        self, customer: CustomerReference | str, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Sale]:
        """List retail sales associated with a specific customer."""
        ...

    def list_by_status(
        self, status: SaleStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Sale]:
        """List retail sales matching a specific lifecycle status."""
        ...

    def count_by_status(self, status: SaleStatus) -> int:
        """Count total retail sales in a given status."""
        ...

    def exists(self, sale_id: SaleId) -> bool:
        """Check if a retail sale exists by ID."""
        ...

    def exists_invoice_number(self, invoice_number: InvoiceNumber) -> bool:
        """Check if an invoice document number is already registered."""
        ...
