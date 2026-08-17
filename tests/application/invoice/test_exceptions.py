"""Unit tests for Invoice application exceptions."""
from __future__ import annotations

from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.application.common import ResourceNotFoundError
from evopharm_retail_erp.application.invoice import InvoiceNotFoundError


class InvoiceExceptionsTests(TestCase):
    def test_invoice_not_found_error_properties(self) -> None:
        inv_id = uuid4()
        err = InvoiceNotFoundError(inv_id)

        self.assertIsInstance(err, ResourceNotFoundError)
        self.assertEqual(err.resource_type, "Invoice")
        self.assertEqual(err.identifier, inv_id)
        self.assertIn(str(inv_id), str(err))
