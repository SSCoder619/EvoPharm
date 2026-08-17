"""Unit tests for Invoice domain enums."""
from __future__ import annotations

from unittest import TestCase

from evopharm_retail_erp.domain.invoice import (
    InvoiceLineStatus,
    InvoiceStatus,
    InvoiceType,
    PaymentStatus,
    TaxType,
)


class InvoiceEnumsTests(TestCase):
    def test_invoice_status_enum_values(self) -> None:
        self.assertEqual(InvoiceStatus.DRAFT.value, "DRAFT")
        self.assertEqual(InvoiceStatus.ISSUED.value, "ISSUED")
        self.assertEqual(InvoiceStatus.PAID.value, "PAID")
        self.assertEqual(InvoiceStatus.PARTIALLY_PAID.value, "PARTIALLY_PAID")
        self.assertEqual(InvoiceStatus.CANCELLED.value, "CANCELLED")
        self.assertEqual(InvoiceStatus.VOID.value, "VOID")

    def test_invoice_type_enum_values(self) -> None:
        self.assertEqual(InvoiceType.TAX_INVOICE.value, "TAX_INVOICE")
        self.assertEqual(InvoiceType.RETAIL_BILL.value, "RETAIL_BILL")
        self.assertEqual(InvoiceType.CREDIT_NOTE.value, "CREDIT_NOTE")
        self.assertEqual(InvoiceType.DEBIT_NOTE.value, "DEBIT_NOTE")

    def test_tax_type_enum_values(self) -> None:
        self.assertEqual(TaxType.INTRA_STATE.value, "INTRA_STATE")
        self.assertEqual(TaxType.INTER_STATE.value, "INTER_STATE")

    def test_payment_status_enum_values(self) -> None:
        self.assertEqual(PaymentStatus.UNPAID.value, "UNPAID")
        self.assertEqual(PaymentStatus.PARTIALLY_PAID.value, "PARTIALLY_PAID")
        self.assertEqual(PaymentStatus.PAID.value, "PAID")

    def test_invoice_line_status_enum_values(self) -> None:
        self.assertEqual(InvoiceLineStatus.ACTIVE.value, "ACTIVE")
        self.assertEqual(InvoiceLineStatus.CANCELLED.value, "CANCELLED")
