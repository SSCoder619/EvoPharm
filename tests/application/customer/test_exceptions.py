"""Unit tests for Customer application exceptions."""
from __future__ import annotations

from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.application.common import ResourceNotFoundError
from evopharm_retail_erp.application.customer import CustomerNotFoundError


class CustomerExceptionsTests(TestCase):
    def test_customer_not_found_error_properties(self) -> None:
        c_id = uuid4()
        err = CustomerNotFoundError(c_id)

        self.assertIsInstance(err, ResourceNotFoundError)
        self.assertEqual(err.resource_type, "Customer")
        self.assertEqual(err.identifier, c_id)
        self.assertIn(str(c_id), str(err))
