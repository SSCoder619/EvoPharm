"""Unit tests for Inventory aggregate root and StockMovement entity."""
from __future__ import annotations

from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.domain.inventory import (
    InsufficientStockError,
    Inventory,
    InventoryId,
    MovementDirection,
    MovementQuantity,
    MovementReason,
    MovementType,
    Quantity,
    SourceDocumentRef,
    SourceDocumentType,
    StockStatus,
    StockThresholds,
)
from evopharm_retail_erp.domain.medicine import MedicineBatchId, MedicineId


class InventoryEntitiesTests(TestCase):
    def setUp(self) -> None:
        self.medicine_id = MedicineId.generate()
        self.batch_id = MedicineBatchId.generate()
        self.inventory = Inventory.create(
            medicine_id=self.medicine_id,
            medicine_batch_id=self.batch_id,
            initial_quantity=Quantity(100),
            thresholds=StockThresholds(
                reorder_level=Quantity(20),
                overstock_level=Quantity(200),
            ),
        )

    def test_initial_state_and_status(self) -> None:
        self.assertEqual(self.inventory.quantity_on_hand.value, 100)
        self.assertEqual(self.inventory.quantity_available.value, 100)
        self.assertEqual(self.inventory.status, StockStatus.IN_STOCK)

    def test_record_receipt_increases_on_hand_and_creates_movement(self) -> None:
        doc = SourceDocumentRef(SourceDocumentType.PURCHASE, uuid4(), "PO-100")
        movement = self.inventory.record_receipt(
            quantity=MovementQuantity(50),
            source_document=doc,
            reason=MovementReason("New purchase batch received"),
        )

        self.assertEqual(self.inventory.quantity_on_hand.value, 150)
        self.assertEqual(len(self.inventory.movements), 1)
        self.assertEqual(movement.movement_type, MovementType.PURCHASE_RECEIPT)
        self.assertEqual(movement.direction, MovementDirection.INBOUND)
        self.assertEqual(movement.quantity.value, 50)

    def test_record_dispense_deducts_stock(self) -> None:
        doc = SourceDocumentRef(SourceDocumentType.SALE, uuid4(), "INV-500")
        movement = self.inventory.record_dispense(
            quantity=MovementQuantity(30),
            source_document=doc,
        )

        self.assertEqual(self.inventory.quantity_on_hand.value, 70)
        self.assertEqual(movement.movement_type, MovementType.SALE_DISPENSE)
        self.assertEqual(movement.direction, MovementDirection.OUTBOUND)

    def test_record_dispense_raises_when_insufficient_stock(self) -> None:
        with self.assertRaises(InsufficientStockError):
            self.inventory.record_dispense(MovementQuantity(150))

    def test_reserve_and_release_stock(self) -> None:
        self.inventory.reserve_stock(MovementQuantity(40))
        self.assertEqual(self.inventory.quantity_on_hand.value, 100)
        self.assertEqual(self.inventory.quantity_reserved.value, 40)
        self.assertEqual(self.inventory.quantity_available.value, 60)

        self.inventory.release_reservation(MovementQuantity(20))
        self.assertEqual(self.inventory.quantity_reserved.value, 20)
        self.assertEqual(self.inventory.quantity_available.value, 80)

    def test_status_transitions_to_low_stock_and_out_of_stock(self) -> None:
        # Deduct down to 15 (reorder level is 20)
        self.inventory.record_dispense(MovementQuantity(85))
        self.assertEqual(self.inventory.status, StockStatus.LOW_STOCK)

        # Deduct remaining 15
        self.inventory.record_dispense(MovementQuantity(15))
        self.assertEqual(self.inventory.status, StockStatus.OUT_OF_STOCK)

    def test_adjust_stock_manually(self) -> None:
        reason = MovementReason("Damaged pack write off")
        self.inventory.adjust_stock(quantity_delta=-10, reason=reason)
        self.assertEqual(self.inventory.quantity_on_hand.value, 90)
