"""Unit tests for Inventory domain events."""
from __future__ import annotations

from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.domain.inventory import (
    InventoryCreated,
    InventoryId,
    LowStockAlertTriggered,
    OutOfStockAlertTriggered,
    Quantity,
    ReorderTriggered,
    StockAdjusted,
    StockDispensed,
    StockMovementId,
    StockReceived,
    StockReleased,
    StockReservationReleased,
    StockReserved,
    StockTransferred,
    StockWrittenOff,
)
from evopharm_retail_erp.domain.medicine import MedicineBatchId, MedicineId


class InventoryDomainEventsTests(TestCase):
    def setUp(self) -> None:
        self.inv_id = InventoryId.generate()
        self.med_id = MedicineId.generate()
        self.batch_id = MedicineBatchId.generate()
        self.movement_id = StockMovementId.generate()

    def test_inventory_created_event(self) -> None:
        event = InventoryCreated(
            inventory_id=self.inv_id,
            medicine_id=self.med_id,
            medicine_batch_id=self.batch_id,
            initial_quantity=Quantity(100),
        )
        self.assertEqual(event.inventory_id, self.inv_id)
        self.assertEqual(event.initial_quantity.value, 100)
        self.assertIsNotNone(event.event_id)
        self.assertIsNotNone(event.occurred_at)

    def test_stock_received_and_dispensed_events(self) -> None:
        received = StockReceived(
            inventory_id=self.inv_id,
            medicine_id=self.med_id,
            medicine_batch_id=self.batch_id,
            movement_id=self.movement_id,
            quantity_received=Quantity(50),
            new_quantity_on_hand=Quantity(150),
        )
        self.assertEqual(received.quantity_received.value, 50)

        dispensed = StockDispensed(
            inventory_id=self.inv_id,
            medicine_id=self.med_id,
            medicine_batch_id=self.batch_id,
            movement_id=self.movement_id,
            quantity_dispensed=Quantity(20),
            new_quantity_on_hand=Quantity(130),
        )
        self.assertEqual(dispensed.quantity_dispensed.value, 20)

    def test_stock_reserved_and_released_events(self) -> None:
        reserved = StockReserved(
            inventory_id=self.inv_id,
            medicine_id=self.med_id,
            medicine_batch_id=self.batch_id,
            quantity_reserved=Quantity(15),
            new_total_reserved=Quantity(15),
        )
        self.assertEqual(reserved.quantity_reserved.value, 15)

        released = StockReleased(
            inventory_id=self.inv_id,
            medicine_id=self.med_id,
            medicine_batch_id=self.batch_id,
            quantity_released=Quantity(5),
            new_total_reserved=Quantity(10),
        )
        self.assertEqual(released.quantity_released.value, 5)

    def test_stock_adjusted_transferred_written_off_events(self) -> None:
        adjusted = StockAdjusted(
            inventory_id=self.inv_id,
            medicine_id=self.med_id,
            medicine_batch_id=self.batch_id,
            movement_id=self.movement_id,
            quantity_delta=-5,
            new_quantity_on_hand=Quantity(95),
            reason="Damaged pack",
        )
        self.assertEqual(adjusted.quantity_delta, -5)

        transferred = StockTransferred(
            inventory_id=self.inv_id,
            medicine_id=self.med_id,
            medicine_batch_id=self.batch_id,
            movement_id=self.movement_id,
            quantity_transferred=Quantity(25),
            destination_reference="DISPENSARY-1",
        )
        self.assertEqual(transferred.destination_reference, "DISPENSARY-1")

        written_off = StockWrittenOff(
            inventory_id=self.inv_id,
            medicine_id=self.med_id,
            medicine_batch_id=self.batch_id,
            movement_id=self.movement_id,
            quantity_written_off=Quantity(10),
            reason="Expired",
        )
        self.assertEqual(written_off.quantity_written_off.value, 10)

    def test_alert_events(self) -> None:
        low_alert = LowStockAlertTriggered(
            inventory_id=self.inv_id,
            medicine_id=self.med_id,
            medicine_batch_id=self.batch_id,
            quantity_available=Quantity(10),
            reorder_level=Quantity(20),
        )
        self.assertEqual(low_alert.reorder_level.value, 20)

        out_alert = OutOfStockAlertTriggered(
            inventory_id=self.inv_id,
            medicine_id=self.med_id,
            medicine_batch_id=self.batch_id,
        )
        self.assertEqual(out_alert.inventory_id, self.inv_id)

    def test_domain_event_immutability(self) -> None:
        event = InventoryCreated(
            inventory_id=self.inv_id,
            medicine_id=self.med_id,
            medicine_batch_id=self.batch_id,
            initial_quantity=Quantity(100),
        )
        with self.assertRaises(Exception):
            event.initial_quantity = Quantity(200)  # type: ignore
