"""Enum definitions for the Customer bounded context.

Every enum here is used across customer entities and value objects to represent a
finite set of valid customer lifecycle states and classification categories.
None of them carry any dependency on infrastructure or presentation concerns —
translating enum values into UI labels or API responses is a job for an outer layer,
not for the domain.
"""
from __future__ import annotations

from enum import Enum, unique


@unique
class CustomerStatus(str, Enum):
    """Lifecycle status of a retail customer aggregate root."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    ARCHIVED = "ARCHIVED"


@unique
class CustomerType(str, Enum):
    """Classification type of customer for pricing, discounts, and benefits."""

    REGULAR = "REGULAR"
    VIP = "VIP"
    SENIOR_CITIZEN = "SENIOR_CITIZEN"
    CORPORATE = "CORPORATE"
