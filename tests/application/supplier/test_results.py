"""Unit tests for Supplier result DTOs."""
from __future__ import annotations

from unittest import TestCase

from evopharm_retail_erp.application.supplier import SupplierResult
from evopharm_retail_erp.domain.supplier import (
    GSTIN,
    PAN,
    Address,
    EmailAddress,
    PhoneNumber,
    PostalCode,
    Supplier,
    SupplierCategory,
    SupplierCode,
    SupplierName,
)


class SupplierResultsTests(TestCase):
    def test_supplier_result_mapping_from_domain(self) -> None:
        supplier = Supplier.register(
            name=SupplierName("Sun Pharma Industries"),
            phone=PhoneNumber("9876543210"),
            code=SupplierCode("SUP-11111"),
            email=EmailAddress("contact@sunpharma.com"),
            address=Address(
                street="1 Sun House",
                city="Mumbai",
                state="Maharashtra",
                postal_code=PostalCode("400063"),
            ),
            gstin=GSTIN("27AAACS1234F1Z0"),
            pan=PAN("AAACS1234F"),
            category=SupplierCategory.MANUFACTURER,
        )

        res = SupplierResult.from_domain(supplier)

        self.assertEqual(res.supplier_id, supplier.id.value)
        self.assertEqual(res.code, "SUP-11111")
        self.assertEqual(res.name, "Sun Pharma Industries")
        self.assertEqual(res.phone, "9876543210")
        self.assertEqual(res.email, "contact@sunpharma.com")
        self.assertIsNotNone(res.address)
        self.assertEqual(res.address.city, "Mumbai")
        self.assertEqual(res.address.pincode, "400063")
        self.assertEqual(res.gstin, "27AAACS1234F1Z0")
        self.assertEqual(res.pan, "AAACS1234F")
        self.assertTrue(res.is_tax_compliant)
        self.assertEqual(res.status, "ACTIVE")
        self.assertEqual(res.category, "MANUFACTURER")
