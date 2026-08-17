"""Unit tests for Inventory command DTOs."""
from __future__ import annotations

from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.application.inventory import (
    AdjustStockCommand,
    DispenseStockCommand,
    ReceiveStockCommand,
    ReleaseStockCommand,
    ReserveStockCommand,
    TransferStockCommand,
    WriteOffStockCommand,
)


class InventoryCommandsTests(TestCase):
    def test_receive_stock_command_instantiation(self) -> None:
        m_id = uuid4()
        b_id = uuid4()
        cmd = ReceiveStockCommand(medicine_id=m_id, medicine_batch_id=b_id, quantity=100)
        self.assertEqual(cmd.medicine_id, m_id)
        self.assertEqual(cmd.medicine_batch_id, b_id)
        self.assertEqual(cmd.quantity, 100)

    def test_reserve_and_release_commands(self) -> None:
        inv_id = uuid4()
        res_cmd = ReserveStockCommand(inventory_id=inv_id, quantity=5)
        rel_cmd = ReleaseStockCommand(inventory_id=inv_id, quantity=5)
        self.assertEqual(res_cmd.inventory_id, inv_id)
        self.assertEqual(rel_cmd.inventory_id, inv_id)

    def test_adjust_and_transfer_commands(self) -> None:
        inv1 = uuid4()
        inv2 = uuid4()
        adj_cmd = AdjustStockCommand(inventory_id=inv1, quantity_delta=-2, reason="Damaged packaging")
        trans_cmd = TransferStockCommand(from_inventory_id=inv1, to_inventory_id=inv2, quantity=10, reason="Store rebalance")

        self.assertEqual(adj_cmd.quantity_delta, -2)
        self.assertEqual(trans_cmd.from_inventory_id, inv1)
        self.assertEqual(trans_cmd.to_inventory_id, inv2)
