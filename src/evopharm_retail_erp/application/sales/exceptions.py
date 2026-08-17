"""Exceptions for the Sales application use-case layer."""
from __future__ import annotations

from uuid import UUID

from ..common.exceptions import ResourceNotFoundError


class SaleNotFoundError(ResourceNotFoundError):
    """Raised when a retail Sale aggregate is not found by ID."""

    def __init__(self, sale_id: UUID) -> None:
        super().__init__("Sale", sale_id)
