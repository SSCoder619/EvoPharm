"""Exceptions for the Application Integration layer."""
from __future__ import annotations

from uuid import UUID

from ..common.exceptions import ApplicationError


class IntegrationError(ApplicationError):
    """Base class for all application integration errors."""


class DuplicateEventError(IntegrationError):
    """Raised when an integration event has already been processed (idempotency guard)."""

    def __init__(self, event_id: UUID) -> None:
        self.event_id = event_id
        super().__init__(f"Integration event {event_id} has already been processed")


class IntegrationMappingError(IntegrationError):
    """Raised when an integration event payload cannot be mapped into a target command."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Integration payload mapping failed: {reason}")
