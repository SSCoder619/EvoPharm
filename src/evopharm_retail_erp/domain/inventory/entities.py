"""Entities for the Inventory bounded context.

Following DDD principles, Inventory is the Aggregate Root representing the current
stock projection for a medicine batch at the pharmacy. StockMovement is an immutable
ledger entry entity that captures historical inventory transactions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

from ..medicine.value_objects import MedicineBatchId, MedicineId
from .enums import (
    MovementDirection,
    MovementType,
    StockStatus,
)
from .exceptions import (
    InsufficientStockError,
    InvalidStockReservationError,
    NegativeStockError,
)
from .value_objects import (
    InventoryId,
    MovementQuantity,
    MovementReason,
    Quantity,
    SourceDocumentRef,
    StockMovementId,
    StockSnapshot,
    StockThresholds,
)


@dataclass(slots=True, eq=False)
class StockMovement:
    """Immutable child entity representing a single stock ledger movement."""

    id: StockMovementId
    inventory_id: InventoryId
    medicine_id: MedicineId
    medicine_batch_id: MedicineBatchId
    movement_type: MovementType
    direction: MovementDirection
    quantity: MovementQuantity
    source_document: SourceDocumentRef | None = None
    reason: MovementReason | None = None
    performed_by_user_id: UUID | None = None
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, StockMovement):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def signed_quantity_delta(self) -> int:
        """Net quantity change on stock (+ for INBOUND, - for OUTBOUND)."""
        if self.direction == MovementDirection.INBOUND:
            return self.quantity.value
        return -self.quantity.value


@dataclass(slots=True, eq=False)
class Inventory:
    """Aggregate Root representing current-stock projection for a medicine batch."""

    id: InventoryId
    medicine_id: MedicineId
    medicine_batch_id: MedicineBatchId
    quantity_on_hand: Quantity = field(default_factory=Quantity.zero)
    quantity_reserved: Quantity = field(default_factory=Quantity.zero)
    thresholds: StockThresholds | None = None
    last_movement_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1
    _movements: list[StockMovement] = field(default_factory=list)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Inventory):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    # -- Factory --------------------------------------------------------

    @classmethod
    def create(
        cls,
        medicine_id: MedicineId,
        medicine_batch_id: MedicineBatchId,
        initial_quantity: Quantity = Quantity.zero(),
        thresholds: StockThresholds | None = None,
        id: InventoryId | None = None,
    ) -> "Inventory":
        """Initialize a new Inventory aggregate root for a medicine batch."""
        inv_id = id if id is not None else InventoryId.generate()
        now = datetime.now(timezone.utc)
        return cls(
            id=inv_id,
            medicine_id=medicine_id,
            medicine_batch_id=medicine_batch_id,
            quantity_on_hand=initial_quantity,
            quantity_reserved=Quantity.zero(),
            thresholds=thresholds,
            last_movement_at=now,
            created_at=now,
            updated_at=now,
        )

    # -- Calculated Properties ------------------------------------------

    @property
    def quantity_available(self) -> Quantity:
        """Stock available for sale or dispensing (On Hand minus Reserved)."""
        return self.quantity_on_hand.subtract(self.quantity_reserved)

    @property
    def status(self) -> StockStatus:
        """Derives current StockStatus based on availability and configured thresholds."""
        avail = self.quantity_available.value
        if avail == 0:
            return StockStatus.OUT_OF_STOCK
        if self.thresholds is not None:
            if self.thresholds.below_reorder_level(avail):
                return StockStatus.LOW_STOCK
            if self.thresholds.is_overstocked(avail):
                return StockStatus.OVERSTOCKED
        return StockStatus.IN_STOCK

    @property
    def overstock_level_value(self) -> int | None:
        if self.thresholds is not None:
            return self.thresholds.overstock_level.value
        return None

    @property
    def is_low_stock(self) -> bool:
        return self.status == StockStatus.LOW_STOCK

    @property
    def is_out_of_stock(self) -> bool:
        return self.status == StockStatus.OUT_OF_STOCK

    @property
    def movements(self) -> tuple[StockMovement, ...]:
        """Read-only view of historical stock movement ledger entries."""
        return tuple(self._movements)

    # -- Internal Helpers -----------------------------------------------

    def _touch(self) -> None:
        """Update timestamp and increment optimistic concurrency version."""
        now = datetime.now(timezone.utc)
        self.last_movement_at = now
        self.updated_at = now
        self.version += 1

    def _append_movement(
        self,
        movement_type: MovementType,
        direction: MovementDirection,
        quantity: MovementQuantity,
        source_document: SourceDocumentRef | None = None,
        reason: MovementReason | None = None,
        performed_by_user_id: UUID | None = None,
    ) -> StockMovement:
        movement = StockMovement(
            id=StockMovementId.generate(),
            inventory_id=self.id,
            medicine_id=self.medicine_id,
            medicine_batch_id=self.medicine_batch_id,
            movement_type=movement_type,
            direction=direction,
            quantity=quantity,
            source_document=source_document,
            reason=reason,
            performed_by_user_id=performed_by_user_id,
        )
        self._movements.append(movement)
        return movement

    # -- Stock Lifecycle Operations -------------------------------------

    def record_receipt(
        self,
        quantity: MovementQuantity,
        source_document: SourceDocumentRef | None = None,
        reason: MovementReason | None = None,
        performed_by_user_id: UUID | None = None,
    ) -> StockMovement:
        """Record received stock (e.g. from purchase or customer return)."""
        self.quantity_on_hand = self.quantity_on_hand.add(quantity.value)
        movement = self._append_movement(
            movement_type=MovementType.PURCHASE_RECEIPT,
            direction=MovementDirection.INBOUND,
            quantity=quantity,
            source_document=source_document,
            reason=reason,
            performed_by_user_id=performed_by_user_id,
        )
        self._touch()
        return movement

    def record_dispense(
        self,
        quantity: MovementQuantity,
        source_document: SourceDocumentRef | None = None,
        reason: MovementReason | None = None,
        performed_by_user_id: UUID | None = None,
    ) -> StockMovement:
        """Record dispensed stock for a retail sale."""
        if quantity.value > self.quantity_available.value:
            raise InsufficientStockError(
                inventory_id=self.id.value,
                requested=quantity.value,
                available=self.quantity_available.value,
            )

        # Deduct from on_hand, and if reserved stock was held, consume reservation
        if self.quantity_reserved.value >= quantity.value:
            self.quantity_reserved = self.quantity_reserved.subtract(quantity.value)
        else:
            self.quantity_reserved = Quantity.zero()

        self.quantity_on_hand = self.quantity_on_hand.subtract(quantity.value)
        movement = self._append_movement(
            movement_type=MovementType.SALE_DISPENSE,
            direction=MovementDirection.OUTBOUND,
            quantity=quantity,
            source_document=source_document,
            reason=reason,
            performed_by_user_id=performed_by_user_id,
        )
        self._touch()
        return movement

    def reserve_stock(self, quantity: MovementQuantity) -> None:
        """Hold stock in reserved state prior to billing completion."""
        if quantity.value > self.quantity_available.value:
            raise InsufficientStockError(
                inventory_id=self.id.value,
                requested=quantity.value,
                available=self.quantity_available.value,
            )
        self.quantity_reserved = self.quantity_reserved.add(quantity.value)
        self._touch()

    def release_reservation(self, quantity: MovementQuantity) -> None:
        """Release previously reserved stock back to available pool."""
        if quantity.value > self.quantity_reserved.value:
            raise InvalidStockReservationError(
                inventory_id=self.id.value,
                reason=f"cannot release {quantity.value} units; only {self.quantity_reserved.value} reserved",
            )
        self.quantity_reserved = self.quantity_reserved.subtract(quantity.value)
        self._touch()

    def adjust_stock(
        self,
        quantity_delta: int,
        reason: MovementReason,
        source_document: SourceDocumentRef | None = None,
        performed_by_user_id: UUID | None = None,
    ) -> StockMovement:
        """Manually adjust inventory for counts, damage, theft, or expiry."""
        if quantity_delta == 0:
            raise NegativeStockError(
                inventory_id=self.id.value,
                current_on_hand=self.quantity_on_hand.value,
                deduction=0,
            )

        if quantity_delta > 0:
            m_qty = MovementQuantity(quantity_delta)
            self.quantity_on_hand = self.quantity_on_hand.add(m_qty.value)
            movement = self._append_movement(
                movement_type=MovementType.STOCK_ADJUSTMENT_ADD,
                direction=MovementDirection.INBOUND,
                quantity=m_qty,
                source_document=source_document,
                reason=reason,
                performed_by_user_id=performed_by_user_id,
            )
        else:
            abs_delta = abs(quantity_delta)
            m_qty = MovementQuantity(abs_delta)
            if abs_delta > self.quantity_on_hand.value:
                raise NegativeStockError(
                    inventory_id=self.id.value,
                    current_on_hand=self.quantity_on_hand.value,
                    deduction=abs_delta,
                )
            self.quantity_on_hand = self.quantity_on_hand.subtract(m_qty.value)
            movement = self._append_movement(
                movement_type=MovementType.STOCK_ADJUSTMENT_DEDUCT,
                direction=MovementDirection.OUTBOUND,
                quantity=m_qty,
                source_document=source_document,
                reason=reason,
                performed_by_user_id=performed_by_user_id,
            )

        self._touch()
        return movement

    def set_thresholds(self, thresholds: StockThresholds) -> None:
        """Update inventory stock level alerts configuration."""
        self.thresholds = thresholds
        self._touch()

    def snapshot(self) -> StockSnapshot:
        """Produce an immutable point-in-time snapshot of current state."""
        return StockSnapshot(
            inventory_id=self.id,
            medicine_id=self.medicine_id,
            medicine_batch_id=self.medicine_batch_id,
            quantity_on_hand=self.quantity_on_hand,
            quantity_reserved=self.quantity_reserved,
            quantity_available=self.quantity_available,
            last_movement_at=self.last_movement_at,
        )
