"""Unit tests for Inventory value objects."""
from __future__ import annotations

from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.domain.inventory import (
    InvalidQuantityError,
    InvalidSourceDocumentRefError,
    InvalidStockThresholdsError,
    MovementQuantity,
    Quantity,
    SourceDocumentRef,
    SourceDocumentType,
    StockThresholds,
)


class InventoryValueObjectsTests(TestCase):
    def test_quantity_creation_and_arithmetic(self) -> None:
        q1 = Quantity(10)
        q2 = Quantity(5)

        self.assertEqual(q1.value, 10)
        self.assertEqual(q1.add(q2).value, 15)
        self.assertEqual(q1.subtract(q2).value, 5)
        self.assertTrue(q1 > q2)
        self.assertTrue(q2 < q1)

    def test_quantity_rejects_negative_or_boolean(self) -> None:
        with self.assertRaises(InvalidQuantityError):
            Quantity(-1)
        with self.assertRaises(InvalidQuantityError):
            Quantity(True)  # type: ignore

    def test_movement_quantity_must_be_strictly_positive(self) -> None:
        self.assertEqual(MovementQuantity(10).value, 10)
        with self.assertRaises(InvalidQuantityError):
            MovementQuantity(0)
        with self.assertRaises(InvalidQuantityError):
            MovementQuantity(-5)

    def test_stock_thresholds_validation(self) -> None:
        thresholds = StockThresholds.create(
            reorder_level=Quantity(10),
            overstock_level=Quantity(100),
            minimum_level=Quantity(2),
        )
        self.assertEqual(thresholds.reorder_level.value, 10)

        with self.assertRaises(InvalidStockThresholdsError):
            StockThresholds(
                reorder_level=Quantity(10),
                overstock_level=Quantity(5),  # overstock <= reorder
            )

    def test_source_document_ref_normalises_text(self) -> None:
        ref = SourceDocumentRef(
            document_type=SourceDocumentType.PURCHASE,
            document_id=uuid4(),
            reference_number="  PO-2026-001  ",
        )
        self.assertEqual(ref.reference_number, "PO-2026-001")

        with self.assertRaises(InvalidSourceDocumentRefError):
            SourceDocumentRef(
                document_type=SourceDocumentType.PURCHASE,
                document_id=uuid4(),
                reference_number="   ",
            )

    def test_quantity_equality(self) -> None:
        self.assertEqual(Quantity(10), Quantity(10))
        self.assertNotEqual(Quantity(10), Quantity(5))

    def test_quantity_hashability(self) -> None:
        quantity_set = {Quantity(10), Quantity(20), Quantity(10)}
        self.assertEqual(len(quantity_set), 2)
        self.assertIn(Quantity(10), quantity_set)

    def test_quantity_underflow(self) -> None:
        with self.assertRaises(InvalidQuantityError):
            Quantity(5).subtract(Quantity(10))

    def test_quantity_immutability(self) -> None:
        q = Quantity(10)
        with self.assertRaises(Exception):
            q.value = 20  # type: ignore

    def test_quantity_boundary_values(self) -> None:
        self.assertEqual(Quantity(0).value, 0)
        self.assertEqual(Quantity(1).value, 1)
        large_q = Quantity(1_000_000_000)
        self.assertEqual(large_q.value, 1_000_000_000)

    def test_stock_threshold_helper_methods(self) -> None:
        thresholds = StockThresholds.create(
            reorder_level=Quantity(10),
            overstock_level=Quantity(100),
            minimum_level=Quantity(2),
        )
        self.assertTrue(thresholds.below_reorder_level(Quantity(5)))
        self.assertTrue(thresholds.below_reorder_level(Quantity(10)))
        self.assertFalse(thresholds.below_reorder_level(Quantity(15)))

        self.assertTrue(thresholds.requires_restock(Quantity(5)))
        self.assertFalse(thresholds.requires_restock(Quantity(20)))

        self.assertTrue(thresholds.is_overstocked(Quantity(150)))
        self.assertFalse(thresholds.is_overstocked(Quantity(50)))

    def test_source_document_ref_normalization_whitespace_characters(self) -> None:
        ref = SourceDocumentRef(
            document_type=SourceDocumentType.PURCHASE,
            document_id=uuid4(),
            reference_number="\tPO-2026-001\n  with \t extra \n spaces   ",
        )
        self.assertEqual(ref.reference_number, "PO-2026-001 with extra spaces")

