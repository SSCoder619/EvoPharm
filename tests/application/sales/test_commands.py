"""Unit tests for Sales command DTOs."""
from __future__ import annotations

from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.application.sales import (
    AddSaleLineCommand,
    AttachPrescriptionCommand,
    CancelSaleCommand,
    CreateSaleCommand,
    ProcessReturnCommand,
    RecordSalePaymentCommand,
)


class SalesCommandsTests(TestCase):
    def test_create_sale_command_instantiation(self) -> None:
        cust_id = uuid4()
        cmd = CreateSaleCommand(customer_id=cust_id, customer_name="Alice Smith", invoice_number="INV-1001")
        self.assertEqual(cmd.customer_id, cust_id)
        self.assertEqual(cmd.customer_name, "Alice Smith")
        self.assertEqual(cmd.invoice_number, "INV-1001")

    def test_add_line_command_instantiation(self) -> None:
        s_id = uuid4()
        m_id = uuid4()
        cmd = AddSaleLineCommand(
            sale_id=s_id,
            medicine_id=m_id,
            quantity=5,
            unit_price=Decimal("200.00"),
        )
        self.assertEqual(cmd.sale_id, s_id)
        self.assertEqual(cmd.medicine_id, m_id)
        self.assertEqual(cmd.quantity, 5)
        self.assertEqual(cmd.unit_price, Decimal("200.00"))

    def test_attach_prescription_and_process_return_commands(self) -> None:
        s_id = uuid4()
        l_id = uuid4()
        rx_cmd = AttachPrescriptionCommand(
            sale_id=s_id,
            prescription_number="RX-999",
            doctor_name="Dr. Mehta",
            doctor_registration_number="REG-12345",
        )
        ret_cmd = ProcessReturnCommand(
            sale_id=s_id,
            line_id=l_id,
            quantity=2,
            reason="WRONG_MEDICINE",
        )
        self.assertEqual(rx_cmd.prescription_number, "RX-999")
        self.assertEqual(ret_cmd.line_id, l_id)
        self.assertEqual(ret_cmd.quantity, 2)
