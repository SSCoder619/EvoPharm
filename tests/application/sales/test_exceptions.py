"""Unit tests for Sales application exceptions."""
from __future__ import annotations

from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.application.common import ResourceNotFoundError
from evopharm_retail_erp.application.sales import SaleNotFoundError


class SalesExceptionsTests(TestCase):
    def test_sale_not_found_error_properties(self) -> None:
        s_id = uuid4()
        err = SaleNotFoundError(s_id)

        self.assertIsInstance(err, ResourceNotFoundError)
        self.assertEqual(err.resource_type, "Sale")
        self.assertEqual(err.identifier, s_id)
        self.assertIn(str(s_id), str(err))
