"""Enum definitions for the Sales bounded context.

Every enum here is used across sales entities and value objects to represent a
finite set of valid retail sales states, payment statuses, and return classifications.
None of them carry any dependency on infrastructure or presentation concerns —
translating enum values into UI labels or API responses is a job for an outer layer,
not for the domain.
"""
from __future__ import annotations

from enum import Enum, unique


@unique
class SaleStatus(str, Enum):
    """Lifecycle status of a retail sale aggregate root."""

    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    PAID = "PAID"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    RETURNED = "RETURNED"


@unique
class PaymentStatus(str, Enum):
    """Commercial payment settlement status of a sale transaction."""

    UNPAID = "UNPAID"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    REFUNDED = "REFUNDED"


@unique
class PaymentMethod(str, Enum):
    """Supported payment settlement instrument methods."""

    CASH = "CASH"
    CARD = "CARD"
    UPI = "UPI"
    NET_BANKING = "NET_BANKING"
    CREDIT = "CREDIT"


@unique
class SaleLineStatus(str, Enum):
    """Fulfillment state of an individual sale line item."""

    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
    CANCELLED = "CANCELLED"


@unique
class ReturnReason(str, Enum):
    """Business justification for processing a customer sale line return."""

    WRONG_MEDICINE = "WRONG_MEDICINE"
    EXPIRED_RECEIVED = "EXPIRED_RECEIVED"
    DAMAGED_PACKAGING = "DAMAGED_PACKAGING"
    CUSTOMER_CHANGED_MIND = "CUSTOMER_CHANGED_MIND"
    OTHER = "OTHER"
