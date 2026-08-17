"""Unit tests for Supplier domain enums."""
from __future__ import annotations

from unittest import TestCase

from evopharm_retail_erp.domain.supplier import SupplierCategory, SupplierStatus


class SupplierEnumsTests(TestCase):
    def test_supplier_status_enum_values(self) -> None:
        self.assertEqual(SupplierStatus.ACTIVE.value, "ACTIVE")
        self.assertEqual(SupplierStatus.INACTIVE.value, "INACTIVE")
        self.assertEqual(SupplierStatus.SUSPENDED.value, "SUSPENDED")
        self.assertEqual(SupplierStatus.ARCHIVED.value, "ARCHIVED")

    def test_supplier_category_enum_values(self) -> None:
        self.assertEqual(SupplierCategory.MANUFACTURER.value, "MANUFACTURER")
        self.assertEqual(SupplierCategory.WHOLESALER.value, "WHOLESALER")
        self.assertEqual(SupplierCategory.DISTRIBUTOR.value, "DISTRIBUTOR")
        self.assertEqual(SupplierCategory.IMPORTER.value, "IMPORTER")
