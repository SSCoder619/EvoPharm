"""Exceptions for the Supplier application use-case layer."""
from __future__ import annotations

from uuid import UUID

from ..common.exceptions import ResourceNotFoundError


class SupplierNotFoundError(ResourceNotFoundError):
    """Raised when a Supplier aggregate is not found by ID."""

    def __init__(self, supplier_id: UUID) -> None:
        super().__init__("Supplier", supplier_id)
