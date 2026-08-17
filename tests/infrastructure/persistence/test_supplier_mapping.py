"""Unit tests for Supplier aggregate <-> ORM mapping."""
from __future__ import annotations

from unittest import TestCase

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
from evopharm_retail_erp.infrastructure.persistence.mappers.supplier_mapper import (
    orm_to_supplier,
    supplier_to_orm,
)


class SupplierMappingTests(TestCase):
    def test_roundtrip_supplier_mapping(self) -> None:
        supplier = Supplier.register(
            name=SupplierName("MedPharma Distributors"),
            phone=PhoneNumber("9876543210"),
            code=SupplierCode("SUP-MED-01"),
            email=EmailAddress("contact@medpharma.com"),
            address=Address(
                street="123 Pharma Way",
                city="Mumbai",
                state="Maharashtra",
                postal_code=PostalCode("400001"),
            ),
            gstin=GSTIN("27ABCDE1234F1Z5"),
            pan=PAN("ABCDE1234F"),
            category=SupplierCategory.WHOLESALER,
        )

        orm = supplier_to_orm(supplier)
        self.assertEqual(orm.code, "SUP-MED-01")
        self.assertEqual(orm.gstin, "27ABCDE1234F1Z5")

        reconstructed = orm_to_supplier(orm)
        self.assertEqual(reconstructed.id, supplier.id)
        self.assertEqual(reconstructed.code.value, "SUP-MED-01")
        self.assertEqual(reconstructed.name.value, "MedPharma Distributors")
        self.assertIsNotNone(reconstructed.gstin)
        self.assertEqual(reconstructed.gstin.value, "27ABCDE1234F1Z5")
        self.assertIsNotNone(reconstructed.address)
        self.assertEqual(reconstructed.address.city, "Mumbai")
