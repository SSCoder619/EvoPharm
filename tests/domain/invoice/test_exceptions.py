"""Unit tests for Invoice domain exceptions hierarchy."""
from __future__ import annotations

from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.domain.invoice import (
    DuplicateInvoiceLineError,
    InvalidInvoiceStateError,
    InvoiceAlreadyCancelledError,
    InvoiceDomainError,
    InvoiceLineNotFoundError,
    OverpaymentError,
)


class InvoiceExceptionsTests(TestCase):
    def test_exception_inheritance_and_messages(self) -> None:
        inv_id = uuid4()
        err_state = InvalidInvoiceStateError(inv_id, "DRAFT", "ISSUED")
        self.assertIsInstance(err_state, InvoiceDomainError)
        self.assertIn(str(inv_id), str(err_state))

        err_cancelled = InvoiceAlreadyCancelledError(inv_id)
        self.assertIsInstance(err_cancelled, InvoiceDomainError)

        err_overpay = OverpaymentError(inv_id, "500.00", "200.00")
        self.assertIsInstance(err_overpay, InvoiceDomainError)
        self.assertIn("exceeds outstanding balance", str(err_overpay))
