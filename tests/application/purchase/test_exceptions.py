"""Unit tests for Purchase application exceptions."""
from __future__ import annotations

from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.application.common import ResourceNotFoundError
from evopharm_retail_erp.application.purchase import PurchaseNotFoundError


class PurchaseExceptionsTests(TestCase):
    def test_purchase_not_found_error_properties(self) -> None:
        p_id = uuid4()
        err = PurchaseNotFoundError(p_id)

        self.assertIsInstance(err, ResourceNotFoundError)
        self.assertEqual(err.resource_type, "Purchase")
        self.assertEqual(err.identifier, p_id)
        self.assertIn(str(p_id), str(err))
