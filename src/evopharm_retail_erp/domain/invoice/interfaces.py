"""Repository interfaces (ports) for the Invoice domain.

These are pure contracts — no implementation, no ORM, no SQL. They define what
the Invoice domain requires from persistence; concrete adapters (SQL, in-memory, etc.)
live in the Infrastructure layer and satisfy these Protocols structurally.
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, TYPE_CHECKING

from .enums import InvoiceStatus
from .value_objects import (
    InvoiceId,
    InvoiceNumber,
    SaleReference,
)

if TYPE_CHECKING:
    from .entities import Invoice


class InvoiceRepository(Protocol):
    """Persistence contract for the Invoice aggregate root.

    Query methods return `Sequence[Invoice]` to ensure callers treat results
    as read-only data.
    """

    def add(self, invoice: Invoice) -> None:
        """Persist a newly created retail invoice aggregate."""
        ...

    def save(self, invoice: Invoice) -> None:
        """Persist modifications to an existing retail invoice aggregate.

        Implementations are expected to use `Invoice.version` for
        optimistic-concurrency control.
        """
        ...

    def get_by_id(self, invoice_id: InvoiceId) -> Invoice | None:
        """Retrieve a retail invoice aggregate by its primary ID."""
        ...

    def get_by_number(self, number: InvoiceNumber) -> Invoice | None:
        """Retrieve a retail invoice matching a unique invoice document number."""
        ...

    def find_by_sale_reference(
        self, sale_reference: SaleReference
    ) -> Invoice | None:
        """Retrieve an invoice corresponding to a source retail Sale transaction."""
        ...

    def list_by_status(
        self, status: InvoiceStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Invoice]:
        """List retail invoices matching a specific status."""
        ...

    def count_by_status(self, status: InvoiceStatus) -> int:
        """Count total retail invoices in a given status."""
        ...

    def exists(self, invoice_id: InvoiceId) -> bool:
        """Check if an invoice exists by ID."""
        ...

    def exists_number(self, number: InvoiceNumber) -> bool:
        """Check if an invoice document number is already registered."""
        ...
