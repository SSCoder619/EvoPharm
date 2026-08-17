"""Enum definitions for the Inventory bounded context.

Every enum here is used across inventory entities and value objects to represent
a finite set of valid stock ledger movement types, source document types, and
inventory statuses. None of them carry any dependency on infrastructure or
presentation concerns — translating enum values into UI labels or API responses is
a job for an outer layer, not for the domain.
"""
from __future__ import annotations

from enum import Enum, unique


@unique
class MovementType(str, Enum):
    """Classification of inventory stock ledger movement events."""

    PURCHASE_RECEIPT = "PURCHASE_RECEIPT"
    SALE_DISPENSE = "SALE_DISPENSE"
    PURCHASE_RETURN = "PURCHASE_RETURN"
    SALE_RETURN = "SALE_RETURN"
    STOCK_ADJUSTMENT_ADD = "STOCK_ADJUSTMENT_ADD"
    STOCK_ADJUSTMENT_DEDUCT = "STOCK_ADJUSTMENT_DEDUCT"
    STOCK_TRANSFER_IN = "STOCK_TRANSFER_IN"
    STOCK_TRANSFER_OUT = "STOCK_TRANSFER_OUT"
    QUARANTINE_HOLD = "QUARANTINE_HOLD"
    QUARANTINE_RELEASE = "QUARANTINE_RELEASE"
    EXPIRY_WRITE_OFF = "EXPIRY_WRITE_OFF"
    RECALL_DISPOSITION = "RECALL_DISPOSITION"
    OPENING_STOCK = "OPENING_STOCK"


@unique
class SourceDocumentType(str, Enum):
    """Domain origin document type associated with a stock movement."""

    PURCHASE = "PURCHASE"
    SALE = "SALE"
    PURCHASE_RETURN = "PURCHASE_RETURN"
    SALE_RETURN = "SALE_RETURN"
    STOCK_ADJUSTMENT = "STOCK_ADJUSTMENT"
    STOCK_TRANSFER = "STOCK_TRANSFER"
    OPENING_BALANCE = "OPENING_BALANCE"
    INVENTORY_AUDIT = "INVENTORY_AUDIT"


@unique
class MovementDirection(str, Enum):
    """Direction of stock quantity change in a ledger entry."""

    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


@unique
class StockStatus(str, Enum):
    """Classification of current availability level for an inventory item."""

    IN_STOCK = "IN_STOCK"
    LOW_STOCK = "LOW_STOCK"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    OVERSTOCKED = "OVERSTOCKED"


@unique
class StockDisposition(str, Enum):
    """Operational allocation state of batch inventory units."""

    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    QUARANTINED = "QUARANTINED"
    EXPIRED = "EXPIRED"
    RECALLED = "RECALLED"
    WRITTEN_OFF = "WRITTEN_OFF"
