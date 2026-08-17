"""Inventory domain package."""
from __future__ import annotations

# Entities
from .entities import Inventory, StockMovement

# Value Objects
from .value_objects import (
    AvailableQuantity,
    InventoryId,
    MovementQuantity,
    MovementReason,
    Quantity,
    ReorderLevel,
    ReservedQuantity,
    SafetyStock,
    SourceDocumentRef,
    StockMovementId,
    StockSnapshot,
    StockThresholds,
)

# Enums
from .enums import (
    MovementDirection,
    MovementType,
    SourceDocumentType,
    StockDisposition,
    StockStatus,
)

# Exceptions
from .exceptions import (
    InsufficientStockError,
    InventoryAlreadyExistsError,
    InventoryDomainError,
    InventoryItemNotFoundError,
    InvalidInventoryStateError,
    InvalidMovementError,
    InvalidMovementReasonError,
    InvalidQuantityError,
    InvalidSourceDocumentRefError,
    InvalidStockReservationError,
    InvalidStockThresholdsError,
    NegativeStockError,
    StockMovementNotFoundError,
)

# Interfaces
from .interfaces import InventoryRepository, StockMovementRepository

# Specifications
from .specifications import (
    AndSpecification,
    CanReserveStockSpecification,
    HasAvailableStockSpecification,
    HasReservedStockSpecification,
    IsLowStockSpecification,
    IsOutOfStockSpecification,
    IsOverstockedSpecification,
    IsStockSufficientSpecification,
    NeedsReorderSpecification,
    NotSpecification,
    OrSpecification,
    OverstockSpecification,
    Specification,
)

# Domain Events
from .domain_events import (
    InventoryCreated,
    InventoryDomainEvent,
    LowStockAlertTriggered,
    OutOfStockAlertTriggered,
    ReorderTriggered,
    StockAdjusted,
    StockDispensed,
    StockReceived,
    StockReleased,
    StockReservationReleased,
    StockReserved,
    StockTransferred,
    StockWrittenOff,
)

# Services
from .services import InventoryReconciliationService, ReconciliationResult

__all__ = [
    "Inventory",
    "StockMovement",
    "AvailableQuantity",
    "InventoryId",
    "MovementQuantity",
    "MovementReason",
    "Quantity",
    "ReorderLevel",
    "ReservedQuantity",
    "SafetyStock",
    "SourceDocumentRef",
    "StockMovementId",
    "StockSnapshot",
    "StockThresholds",
    "MovementDirection",
    "MovementType",
    "SourceDocumentType",
    "StockDisposition",
    "StockStatus",
    "InsufficientStockError",
    "InventoryAlreadyExistsError",
    "InventoryDomainError",
    "InventoryItemNotFoundError",
    "InvalidInventoryStateError",
    "InvalidMovementError",
    "InvalidMovementReasonError",
    "InvalidQuantityError",
    "InvalidSourceDocumentRefError",
    "InvalidStockReservationError",
    "InvalidStockThresholdsError",
    "NegativeStockError",
    "StockMovementNotFoundError",
    "InventoryRepository",
    "StockMovementRepository",
    "AndSpecification",
    "CanReserveStockSpecification",
    "HasAvailableStockSpecification",
    "HasReservedStockSpecification",
    "IsLowStockSpecification",
    "IsOutOfStockSpecification",
    "IsOverstockedSpecification",
    "IsStockSufficientSpecification",
    "NeedsReorderSpecification",
    "NotSpecification",
    "OrSpecification",
    "OverstockSpecification",
    "Specification",
    "InventoryCreated",
    "InventoryDomainEvent",
    "LowStockAlertTriggered",
    "OutOfStockAlertTriggered",
    "ReorderTriggered",
    "StockAdjusted",
    "StockDispensed",
    "StockReceived",
    "StockReleased",
    "StockReservationReleased",
    "StockReserved",
    "StockTransferred",
    "StockWrittenOff",
    "InventoryReconciliationService",
    "ReconciliationResult",
]
