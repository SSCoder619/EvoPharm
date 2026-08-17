"""Unit tests for Supplier application exceptions."""
from __future__ import annotations

from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.application.common import ResourceNotFoundError
from evopharm_retail_erp.application.supplier import SupplierNotFoundError


class SupplierExceptionsTests(TestCase):
    def test_supplier_not_found_error_properties(self) -> None:
        s_id = uuid4()
        err = SupplierNotFoundError(s_id)

        self.assertIsInstance(err, ResourceNotFoundError)
        self.assertEqual(err.resource_type, "Supplier")
        self.assertEqual(err.identifier, s_id)
        self.assertIn(str(s_id), str(err))
