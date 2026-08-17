"""Immutable value objects owned by the Inventory bounded context.

Validation and normalization rules live here so the aggregate root and entities never accept
primitive strings or invalid numeric values for inventory state. These types deliberately
depend on no database, UI framework, or outer application layer.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from ..medicine.value_objects import MedicineBatchId, MedicineId
from .enums import SourceDocumentType
from .exceptions import (
    InvalidMovementReasonError,
    InvalidQuantityError,
    InvalidSourceDocumentRefError,
    InvalidStockThresholdsError,
)


def _normalise_text(value: str) -> str:
    return " ".join(value.split())


@dataclass(frozen=True, slots=True)
class InventoryId:
    """Stable identity of an Inventory aggregate root."""

    value: UUID

    @classmethod
    def generate(cls) -> "InventoryId":
        return cls(uuid4())

    @classmethod
    def from_string(cls, value: str) -> "InventoryId":
        return cls(UUID(value))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class StockMovementId:
    """Stable identity of a StockMovement ledger entity."""

    value: UUID

    @classmethod
    def generate(cls) -> "StockMovementId":
        return cls(uuid4())

    @classmethod
    def from_string(cls, value: str) -> "StockMovementId":
        return cls(UUID(value))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class Quantity:
    """Non-negative integer stock quantity value object."""

    value: int

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not isinstance(self.value, int):
            raise InvalidQuantityError(self.value, "quantity must be an integer")
        if self.value < 0:
            raise InvalidQuantityError(self.value, "quantity cannot be negative")

    @classmethod
    def zero(cls) -> "Quantity":
        return cls(0)

    def add(self, amount: int | Quantity) -> "Quantity":
        add_val = amount.value if isinstance(amount, Quantity) else amount
        return Quantity(self.value + add_val)

    def subtract(self, amount: int | Quantity) -> "Quantity":
        sub_val = amount.value if isinstance(amount, Quantity) else amount
        if sub_val > self.value:
            raise InvalidQuantityError(
                self.value, f"cannot subtract {sub_val} from {self.value}"
            )
        return Quantity(self.value - sub_val)

    def increase(self, amount: int | Quantity) -> "Quantity":
        return self.add(amount)

    def decrease(self, amount: int | Quantity) -> "Quantity":
        return self.subtract(amount)

    def is_zero(self) -> bool:
        return self.value == 0

    @property
    def is_empty(self) -> bool:
        return self.value == 0

    def is_positive(self) -> bool:
        return self.value > 0

    def __lt__(self, other: object) -> bool:
        if isinstance(other, Quantity):
            return self.value < other.value
        if isinstance(other, int):
            return self.value < other
        return NotImplemented

    def __le__(self, other: object) -> bool:
        if isinstance(other, Quantity):
            return self.value <= other.value
        if isinstance(other, int):
            return self.value <= other
        return NotImplemented

    def __gt__(self, other: object) -> bool:
        if isinstance(other, Quantity):
            return self.value > other.value
        if isinstance(other, int):
            return self.value > other
        return NotImplemented

    def __ge__(self, other: object) -> bool:
        if isinstance(other, Quantity):
            return self.value >= other.value
        if isinstance(other, int):
            return self.value >= other
        return NotImplemented

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class AvailableQuantity(Quantity):
    """Semantic value object representing stock available for sellable allocation."""

    def can_fulfil(self, requested: Quantity | int) -> bool:
        req_val = requested.value if isinstance(requested, Quantity) else requested
        return self.value >= req_val


@dataclass(frozen=True, slots=True)
class ReservedQuantity(Quantity):
    """Semantic value object representing stock currently held in reservation."""


@dataclass(frozen=True, slots=True)
class SafetyStock(Quantity):
    """Minimum safety threshold below which stock should not fall."""


@dataclass(frozen=True, slots=True)
class ReorderLevel(Quantity):
    """Stock level threshold that triggers automatic replenishment alerts."""


@dataclass(frozen=True, slots=True)
class MovementQuantity:
    """Strictly positive integer quantity for inventory ledger changes."""

    value: int

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not isinstance(self.value, int):
            raise InvalidQuantityError(self.value, "movement quantity must be an integer")
        if self.value <= 0:
            raise InvalidQuantityError(
                self.value, "movement quantity must be strictly positive (> 0)"
            )

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class StockThresholds:
    """Configurable reorder and overstock warning thresholds for inventory control."""

    reorder_level: ReorderLevel
    overstock_level: Quantity
    safety_stock: SafetyStock = SafetyStock(0)

    def __post_init__(self) -> None:
        if not isinstance(self.reorder_level, ReorderLevel):
            r_val = self.reorder_level.value if isinstance(self.reorder_level, Quantity) else self.reorder_level
            object.__setattr__(self, "reorder_level", ReorderLevel(r_val))
        if not isinstance(self.safety_stock, SafetyStock):
            s_val = self.safety_stock.value if isinstance(self.safety_stock, Quantity) else self.safety_stock
            object.__setattr__(self, "safety_stock", SafetyStock(s_val))
        if self.safety_stock.value > self.reorder_level.value:
            raise InvalidStockThresholdsError(
                f"safety stock ({self.safety_stock.value}) cannot exceed reorder level ({self.reorder_level.value})"
            )
        if self.reorder_level.value >= self.overstock_level.value:
            raise InvalidStockThresholdsError(
                f"reorder level ({self.reorder_level.value}) must be strictly less than overstock level ({self.overstock_level.value})"
            )

    @classmethod
    def create(
        cls,
        reorder_level: int | Quantity,
        overstock_level: int | Quantity,
        minimum_level: int | Quantity = 0,
    ) -> "StockThresholds":
        r_val = reorder_level.value if isinstance(reorder_level, Quantity) else reorder_level
        o_val = overstock_level.value if isinstance(overstock_level, Quantity) else overstock_level
        m_val = minimum_level.value if isinstance(minimum_level, Quantity) else minimum_level
        return cls(
            reorder_level=ReorderLevel(r_val),
            overstock_level=Quantity(o_val),
            safety_stock=SafetyStock(m_val),
        )

    @property
    def minimum_level(self) -> SafetyStock:
        return self.safety_stock

    def below_reorder_level(self, available: Quantity | int) -> bool:
        avail_val = available.value if isinstance(available, Quantity) else available
        return avail_val <= self.reorder_level.value

    def requires_restock(self, available: Quantity | int) -> bool:
        return self.below_reorder_level(available)

    def is_overstocked(self, available: Quantity | int) -> bool:
        avail_val = available.value if isinstance(available, Quantity) else available
        return avail_val > self.overstock_level.value


@dataclass(frozen=True, slots=True)
class SourceDocumentRef:
    """Typed link connecting a stock movement to its originating commercial document."""

    document_type: SourceDocumentType
    document_id: UUID
    reference_number: str

    def __post_init__(self) -> None:
        cleaned_ref = _normalise_text(self.reference_number)
        if not cleaned_ref:
            raise InvalidSourceDocumentRefError("reference number cannot be empty")
        if len(cleaned_ref) > 100:
            raise InvalidSourceDocumentRefError("reference number must be at most 100 characters")
        object.__setattr__(self, "reference_number", cleaned_ref)


@dataclass(frozen=True, slots=True)
class MovementReason:
    """Business justification or operational note attached to a stock movement."""

    description: str

    def __post_init__(self) -> None:
        cleaned = _normalise_text(self.description)
        if not cleaned:
            raise InvalidMovementReasonError("movement reason description is required")
        if len(cleaned) > 250:
            raise InvalidMovementReasonError("movement reason description must be at most 250 characters")
        object.__setattr__(self, "description", cleaned)

    def __str__(self) -> str:
        return self.description


@dataclass(frozen=True, slots=True)
class StockSnapshot:
    """Immutable point-in-time state of an inventory aggregate."""

    inventory_id: InventoryId
    medicine_id: MedicineId
    medicine_batch_id: MedicineBatchId
    quantity_on_hand: Quantity
    quantity_reserved: ReservedQuantity
    quantity_available: AvailableQuantity
    last_movement_at: datetime
