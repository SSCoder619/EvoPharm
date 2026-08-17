"""Exceptions for the Invoice application use-case layer."""
from __future__ import annotations

from uuid import UUID

from ..common.exceptions import ResourceNotFoundError


class InvoiceNotFoundError(ResourceNotFoundError):
    """Raised when an Invoice aggregate is not found by ID."""

    def __init__(self, invoice_id: UUID) -> None:
        super().__init__("Invoice", invoice_id)
