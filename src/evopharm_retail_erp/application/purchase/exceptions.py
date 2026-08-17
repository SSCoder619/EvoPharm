"""Exceptions for the Purchase application use-case layer."""
from __future__ import annotations

from uuid import UUID

from ..common.exceptions import ResourceNotFoundError


class PurchaseNotFoundError(ResourceNotFoundError):
    """Raised when a Purchase Order aggregate is not found by ID."""

    def __init__(self, purchase_id: UUID) -> None:
        super().__init__("Purchase", purchase_id)
