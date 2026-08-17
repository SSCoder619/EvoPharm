"""Enum definitions for the Purchase bounded context.

Every enum here is used across purchase entities and value objects to represent
a finite set of valid procurement states, receiving progress, and payment statuses.
None of them carry any dependency on infrastructure or presentation concerns —
translating enum values into UI labels or API responses is a job for an outer layer,
not for the domain.
"""
from __future__ import annotations

from enum import Enum, unique


@unique
class PurchaseStatus(str, Enum):
    """Lifecycle status of a procurement purchase order aggregate."""

    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    ORDERED = "ORDERED"
    PARTIALLY_RECEIVED = "PARTIALLY_RECEIVED"
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


@unique
class ReceivingStatus(str, Enum):
    """Execution status of physical inventory receiving against a purchase order."""

    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


@unique
class PaymentStatus(str, Enum):
    """Commercial payment settlement status of a purchase order."""

    UNPAID = "UNPAID"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    REFUNDED = "REFUNDED"


@unique
class PurchaseLineStatus(str, Enum):
    """Fulfillment state of an individual purchase order line item."""

    PENDING = "PENDING"
    PARTIALLY_RECEIVED = "PARTIALLY_RECEIVED"
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"
