"""Exceptions for the Customer application use-case layer."""
from __future__ import annotations

from uuid import UUID

from ..common.exceptions import ResourceNotFoundError


class CustomerNotFoundError(ResourceNotFoundError):
    """Raised when a Customer aggregate is not found by ID."""

    def __init__(self, customer_id: UUID) -> None:
        super().__init__("Customer", customer_id)
