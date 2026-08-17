"""Repository interfaces (ports) for the Supplier domain.

These are pure contracts — no implementation, no ORM, no SQL. They define what
the Supplier domain requires from persistence; concrete adapters (SQL, in-memory, etc.)
live in the Infrastructure layer and satisfy these Protocols structurally.
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, TYPE_CHECKING

from .enums import SupplierStatus
from .value_objects import (
    GSTIN,
    SupplierCode,
    SupplierId,
)

if TYPE_CHECKING:
    from .entities import Supplier


class SupplierRepository(Protocol):
    """Persistence contract for the Supplier aggregate root.

    Query methods return `Sequence[Supplier]` to ensure callers treat results
    as read-only data.
    """

    def add(self, supplier: Supplier) -> None:
        """Persist a newly registered supplier aggregate."""
        ...

    def save(self, supplier: Supplier) -> None:
        """Persist modifications to an existing supplier aggregate.

        Implementations are expected to use `Supplier.version` for
        optimistic-concurrency control.
        """
        ...

    def get_by_id(self, supplier_id: SupplierId) -> Supplier | None:
        """Retrieve a supplier aggregate by its primary ID."""
        ...

    def get_by_code(self, code: SupplierCode) -> Supplier | None:
        """Retrieve a supplier aggregate by unique supplier code."""
        ...

    def get_by_gstin(self, gstin: GSTIN) -> Supplier | None:
        """Retrieve a supplier aggregate by GSTIN compliance identifier."""
        ...

    def list_by_status(
        self, status: SupplierStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Supplier]:
        """List supplier aggregates matching a specific status."""
        ...

    def count_by_status(self, status: SupplierStatus) -> int:
        """Count total supplier records in a given status."""
        ...

    def exists(self, supplier_id: SupplierId) -> bool:
        """Check if a supplier exists by ID."""
        ...

    def exists_code(self, code: SupplierCode) -> bool:
        """Check if a supplier code is already registered."""
        ...
