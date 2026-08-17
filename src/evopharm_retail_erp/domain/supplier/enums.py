"""Enum definitions for the Supplier bounded context.

Every enum here is used across supplier entities and value objects to represent a
finite set of valid supplier lifecycle states and classification categories.
None of them carry any dependency on infrastructure or presentation concerns —
translating enum values into UI labels or API responses is a job for an outer layer,
not for the domain.
"""
from __future__ import annotations

from enum import Enum, unique


@unique
class SupplierStatus(str, Enum):
    """Lifecycle status of a pharmaceutical supplier aggregate root."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    ARCHIVED = "ARCHIVED"


@unique
class SupplierCategory(str, Enum):
    """Business classification category of a supplier."""

    MANUFACTURER = "MANUFACTURER"
    WHOLESALER = "WHOLESALER"
    DISTRIBUTOR = "DISTRIBUTOR"
    IMPORTER = "IMPORTER"
