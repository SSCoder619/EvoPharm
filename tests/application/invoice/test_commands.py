"""Unit tests for Invoice command DTOs."""
from __future__ import annotations

from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.application.invoice import (
    AddInvoiceLineCommand,
    CancelInvoiceCommand,
    CreateInvoiceCommand,
    IssueInvoiceCommand,
    RecordInvoicePaymentCommand,
)


class InvoiceCommandsTests(TestCase):
    def test_create_invoice_command_instantiation(self) -> None:
        sale_id = uuid4()
        cmd = CreateInvoiceCommand(
            sale_id=sale_id,
            sale_invoice_number="INV-SALE-001",
            customer_name="Apollo Pharmacy",
            customer_gstin="27AABCU9603R1ZN",
            tax_type="INTER_STATE",
        )
        self.assertEqual(cmd.sale_id, sale_id)
        self.assertEqual(cmd.customer_name, "Apollo Pharmacy")
        self.assertEqual(cmd.tax_type, "INTER_STATE")

    def test_add_line_command_instantiation(self) -> None:
        inv_id = uuid4()
        m_id = uuid4()
        cmd = AddInvoiceLineCommand(
            invoice_id=inv_id,
            medicine_id=m_id,
            quantity=10,
            unit_price=Decimal("100.00"),
            tax_rate_percentage=Decimal("18.00"),
        )
        self.assertEqual(cmd.invoice_id, inv_id)
        self.assertEqual(cmd.medicine_id, m_id)
        self.assertEqual(cmd.quantity, 10)
        self.assertEqual(cmd.tax_rate_percentage, Decimal("18.00"))

    def test_issue_payment_cancel_commands(self) -> None:
        inv_id = uuid4()
        iss_cmd = IssueInvoiceCommand(invoice_id=inv_id)
        pay_cmd = RecordInvoicePaymentCommand(invoice_id=inv_id, amount_paid=Decimal("500.00"))
        can_cmd = CancelInvoiceCommand(invoice_id=inv_id, reason="Billing correction")

        self.assertEqual(iss_cmd.invoice_id, inv_id)
        self.assertEqual(pay_cmd.amount_paid, Decimal("500.00"))
        self.assertEqual(can_cmd.reason, "Billing correction")
