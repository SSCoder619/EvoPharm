"""Application-layer ports for infrastructure capabilities.

Defines structural Protocol interfaces for cross-cutting services required by use-case handlers
(e.g., time provider, ID generator, event dispatcher).
"""
from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID


class ClockPort(Protocol):
    """Port for obtaining current date and time."""

    def now_utc(self) -> datetime:
        """Return current timestamp in UTC timezone."""
        ...


class IdGeneratorPort(Protocol):
    """Port for generating unique identifiers."""

    def generate_uuid(self) -> UUID:
        """Generate a new random UUID."""
        ...


class EventDispatcherPort(Protocol):
    """Port for dispatching domain/application events."""

    async def publish(self, event: object) -> None:
        """Publish a single event to registered handlers."""
        ...

    async def publish_all(self, events: tuple[object, ...] | list[object]) -> None:
        """Publish a sequence of events to registered handlers."""
        ...
