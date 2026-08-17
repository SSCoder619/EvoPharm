"""Unit tests for Purchase command DTOs."""
from __future__ import annotations

from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.application.purchase import (
    AddPurchaseLineCommand,
    ApprovePurchaseCommand,
    CancelPurchaseCommand,
    CreatePurchaseCommand,
    PlacePurchaseOrderCommand,
    ReceivePurchaseStockCommand,
)


class PurchaseCommandsTests(TestCase):
    def test_create_purchase_command_instantiation(self) -> None:
        sup_id = uuid4()
        cmd = CreatePurchaseCommand(supplier_id=sup_id, order_reference="PO-1001")
        self.assertEqual(cmd.supplier_id, sup_id)
        self.assertEqual(cmd.order_reference, "PO-1001")

    def test_add_line_command_instantiation(self) -> None:
        p_id = uuid4()
        m_id = uuid4()
        cmd = AddPurchaseLineCommand(
            purchase_id=p_id,
            medicine_id=m_id,
            ordered_quantity=10,
            unit_price=Decimal("150.00"),
        )
        self.assertEqual(cmd.purchase_id, p_id)
        self.assertEqual(cmd.medicine_id, m_id)
        self.assertEqual(cmd.ordered_quantity, 10)
        self.assertEqual(cmd.unit_price, Decimal("150.00"))

    def test_receive_stock_command_instantiation(self) -> None:
        p_id = uuid4()
        l_id = uuid4()
        cmd = ReceivePurchaseStockCommand(
            purchase_id=p_id,
            line_id=l_id,
            quantity=5,
            batch_number="BATCH-99",
        )
        self.assertEqual(cmd.purchase_id, p_id)
        self.assertEqual(cmd.line_id, l_id)
        self.assertEqual(cmd.quantity, 5)
        self.assertEqual(cmd.batch_number, "BATCH-99")
