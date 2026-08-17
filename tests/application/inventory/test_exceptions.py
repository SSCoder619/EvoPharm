"""Unit tests for Inventory application exceptions."""
from __future__ import annotations

from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.application.common import ResourceNotFoundError
from evopharm_retail_erp.application.inventory import InventoryNotFoundError


class InventoryExceptionsTests(TestCase):
    def test_inventory_not_found_error_properties(self) -> None:
        inv_id = uuid4()
        err = InventoryNotFoundError(inv_id)

        self.assertIsInstance(err, ResourceNotFoundError)
        self.assertEqual(err.resource_type, "Inventory")
        self.assertEqual(err.identifier, inv_id)
        self.assertIn(str(inv_id), str(err))
