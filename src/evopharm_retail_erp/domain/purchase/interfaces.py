"""Repository interfaces (ports) for the Purchase domain.

These are pure contracts — no implementation, no ORM, no SQL. They define what
the Purchase domain requires from persistence; concrete adapters (SQL, in-memory, etc.)
live in the Infrastructure layer and satisfy these Protocols structurally.
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from .enums import PurchaseStatus, ReceivingStatus
from .value_objects import (
    InvoiceReference,
    PurchaseId,
    PurchaseOrderReference,
    SupplierReference,
)
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .entities import Purchase


class PurchaseRepository(Protocol):
    """Persistence contract for the Purchase aggregate root.

    Query methods return `Sequence[Purchase]` to ensure callers treat results
    as read-only data.
    """

    def add(self, purchase: Purchase) -> None:
        """Persist a newly created purchase order aggregate."""
        ...

    def save(self, purchase: Purchase) -> None:
        """Persist modifications to an existing purchase order aggregate.

        Implementations are expected to use `Purchase.version` for
        optimistic-concurrency control.
        """
        ...

    def get_by_id(self, purchase_id: PurchaseId) -> Purchase | None:
        """Retrieve a purchase order aggregate by its primary ID."""
        ...

    def get_by_order_reference(
        self, order_reference: PurchaseOrderReference
    ) -> Purchase | None:
        """Retrieve a purchase order matching a unique order reference number."""
        ...

    def get_by_invoice_reference(
        self, invoice_reference: InvoiceReference
    ) -> Purchase | None:
        """Retrieve a purchase order matching an attached commercial invoice reference."""
        ...

    def list_by_supplier(
        self, supplier_id: SupplierReference | str, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Purchase]:
        """List purchase orders associated with a specific supplier."""
        ...

    def list_by_status(
        self, status: PurchaseStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Purchase]:
        """List purchase orders matching a specific lifecycle status."""
        ...

    def list_by_receiving_status(
        self, receiving_status: ReceivingStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Purchase]:
        """List purchase orders matching a specific receiving status."""
        ...

    def count_by_status(self, status: PurchaseStatus) -> int:
        """Count total purchase orders in a given status."""
        ...

    def exists(self, purchase_id: PurchaseId) -> bool:
        """Check if a purchase order exists by ID."""
        ...

    def exists_order_reference(self, order_reference: PurchaseOrderReference) -> bool:
        """Check if a purchase order reference number is already registered."""
        ...
