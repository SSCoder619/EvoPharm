"""Application Integration package."""
from __future__ import annotations

from .events import (
    IntegrationEvent,
    InvoicePaidPayload,
    PurchaseReceivedPayload,
    SaleCompletedPayload,
    SaleReturnedPayload,
)
from .exceptions import (
    DuplicateEventError,
    IntegrationError,
    IntegrationMappingError,
)
from .handlers import (
    EventTracker,
    InMemoryEventTracker,
    InvoicePaidHandler,
    PurchaseReceivedHandler,
    SaleCompletedHandler,
    SaleReturnedHandler,
)

__all__ = [
    "IntegrationEvent",
    "PurchaseReceivedPayload",
    "SaleCompletedPayload",
    "SaleReturnedPayload",
    "InvoicePaidPayload",
    "IntegrationError",
    "DuplicateEventError",
    "IntegrationMappingError",
    "EventTracker",
    "InMemoryEventTracker",
    "PurchaseReceivedHandler",
    "SaleCompletedHandler",
    "SaleReturnedHandler",
    "InvoicePaidHandler",
]
