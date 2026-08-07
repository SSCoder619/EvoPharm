"""Enum definitions for the Medicine bounded context.

Every enum here is used across entities and value objects to represent a
finite set of valid states or categories. None of them carry any dependency on
infrastructure or presentation concerns (no dynamic value generation, no ORM
mapping logic) — translating enum values into UI labels or API responses is
a job for an outer layer, not for the domain.
"""
from __future__ import annotations

from enum import Enum, unique


@unique
class BatchStatus(str, Enum):
    """Lifecycle status of a medicine batch."""

    ACTIVE = "ACTIVE"
    QUARANTINED = "QUARANTINED"
    EXPIRED = "EXPIRED"
    RECALLED = "RECALLED"
    CONSUMED = "CONSUMED"


@unique
class BatchSource(str, Enum):
    """Origin channel through which a batch entered inventory."""

    PURCHASE = "PURCHASE"
    CUSTOMER_RETURN = "CUSTOMER_RETURN"
    SUPPLIER_REPLACEMENT = "SUPPLIER_REPLACEMENT"
    STOCK_ADJUSTMENT = "STOCK_ADJUSTMENT"
    OPENING_STOCK = "OPENING_STOCK"


@unique
class QuarantineReason(str, Enum):
    """Business justification for placing a batch under quarantine."""

    PENDING_QUALITY_CHECK = "PENDING_QUALITY_CHECK"
    DAMAGED_PACKAGING = "DAMAGED_PACKAGING"
    TEMPERATURE_EXCURSION = "TEMPERATURE_EXCURSION"
    SUSPECTED_COUNTERFEIT = "SUSPECTED_COUNTERFEIT"
    REGULATORY_HOLD = "REGULATORY_HOLD"
    RECALL_INVESTIGATION = "RECALL_INVESTIGATION"


@unique
class StockAdjustmentReason(str, Enum):
    """Business justification for manual inventory adjustments."""

    PHYSICAL_COUNT_VARIANCE = "PHYSICAL_COUNT_VARIANCE"
    DAMAGE = "DAMAGE"
    THEFT_OR_LOSS = "THEFT_OR_LOSS"
    EXPIRY_WRITE_OFF = "EXPIRY_WRITE_OFF"
    CORRECTION = "CORRECTION"