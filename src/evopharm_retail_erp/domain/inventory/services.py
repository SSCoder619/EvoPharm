"""Domain services for the Inventory bounded context.

Domain services are implemented only when business logic naturally spans multiple
aggregates or requires computing ledger reconciliation outside a single aggregate boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Sequence

from .entities import Inventory, StockMovement
from .enums import MovementDirection
from .value_objects import Quantity


@dataclass(frozen=True, slots=True)
class ReconciliationResult:
    """Result of comparing an inventory projection against its stock ledger movements."""

    inventory_id: str
    expected_on_hand: Quantity
    actual_on_hand: Quantity
    discrepancy: int

    @property
    def is_consistent(self) -> bool:
        return self.discrepancy == 0


class InventoryReconciliationService:
    """Domain service that verifies projection integrity against ledger movements.

    Performs a mathematical audit of an Inventory aggregate by summing all
    inbound and outbound StockMovement ledger entries to compute the expected
    stock on hand.
    """

    def reconcile(
        self,
        inventory: Inventory,
        movements: Sequence[StockMovement],
    ) -> ReconciliationResult:
        """Reconcile inventory projection against stock ledger entries."""
        total_delta = 0
        for movement in movements:
            if movement.inventory_id == inventory.id:
                if movement.direction == MovementDirection.INBOUND:
                    total_delta += movement.quantity.value
                else:
                    total_delta -= movement.quantity.value

        expected_on_hand = Quantity(max(0, total_delta))
        actual_on_hand = inventory.quantity_on_hand
        discrepancy = actual_on_hand.value - expected_on_hand.value

        return ReconciliationResult(
            inventory_id=str(inventory.id),
            expected_on_hand=expected_on_hand,
            actual_on_hand=actual_on_hand,
            discrepancy=discrepancy,
        )
