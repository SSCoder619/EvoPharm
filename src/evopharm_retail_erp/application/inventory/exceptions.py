"""Exceptions for the Inventory application use-case layer."""
from __future__ import annotations

from uuid import UUID

from ..common.exceptions import ResourceNotFoundError


class InventoryNotFoundError(ResourceNotFoundError):
    """Raised when an Inventory aggregate projection is not found by ID."""

    def __init__(self, inventory_id: UUID) -> None:
        super().__init__("Inventory", inventory_id)
