"""Unit tests for Supplier aggregate root."""
from __future__ import annotations

from unittest import TestCase

from evopharm_retail_erp.domain.supplier import (
    GSTIN,
    PAN,
    Address,
    EmailAddress,
    InvalidSupplierStateError,
    PhoneNumber,
    PostalCode,
    Supplier,
    SupplierAlreadyActiveError,
    SupplierAlreadyInactiveError,
    SupplierCategory,
    SupplierName,
    SupplierStatus,
)


class SupplierEntitiesTests(TestCase):
    def setUp(self) -> None:
        self.name = SupplierName("Zenith Healthcare")
        self.phone = PhoneNumber("+919876543210")
        self.email = EmailAddress("contact@zenithpharma.com")
        self.gstin = GSTIN("29ABCDE1234F1Z5")
        self.pan = PAN("ABCDE1234F")
        self.supplier = Supplier.register(
            name=self.name,
            phone=self.phone,
            email=self.email,
            gstin=self.gstin,
            pan=self.pan,
            category=SupplierCategory.MANUFACTURER,
        )

    def test_registration_initial_state(self) -> None:
        self.assertEqual(self.supplier.name, self.name)
        self.assertEqual(self.supplier.phone, self.phone)
        self.assertEqual(self.supplier.email, self.email)
        self.assertEqual(self.supplier.gstin, self.gstin)
        self.assertEqual(self.supplier.pan, self.pan)
        self.assertEqual(self.supplier.status, SupplierStatus.ACTIVE)
        self.assertEqual(self.supplier.category, SupplierCategory.MANUFACTURER)
        self.assertTrue(self.supplier.is_active)
        self.assertTrue(self.supplier.is_tax_compliant)

    def test_lifecycle_deactivate_and_activate(self) -> None:
        self.supplier.deactivate("Supplier merged")
        self.assertEqual(self.supplier.status, SupplierStatus.INACTIVE)
        self.assertFalse(self.supplier.is_active)

        with self.assertRaises(SupplierAlreadyInactiveError):
            self.supplier.deactivate("Double deactivate")

        self.supplier.activate("Renewed partnership")
        self.assertEqual(self.supplier.status, SupplierStatus.ACTIVE)

        with self.assertRaises(SupplierAlreadyActiveError):
            self.supplier.activate()

    def test_suspend_and_reactivate(self) -> None:
        self.supplier.suspend("Quality audit failure")
        self.assertEqual(self.supplier.status, SupplierStatus.SUSPENDED)

        with self.assertRaises(InvalidSupplierStateError):
            self.supplier.activate()

        self.supplier.reactivate("Quality audit cleared")
        self.assertEqual(self.supplier.status, SupplierStatus.ACTIVE)

    def test_archive_account(self) -> None:
        self.supplier.archive("Business ceased operation")
        self.assertEqual(self.supplier.status, SupplierStatus.ARCHIVED)

        with self.assertRaises(InvalidSupplierStateError):
            self.supplier.activate()

    def test_update_contact_information(self) -> None:
        new_phone = PhoneNumber("+919988776655")
        new_email = EmailAddress("orders@zenithpharma.com")

        self.supplier.update_contact_information(new_phone, new_email)
        self.assertEqual(self.supplier.phone, new_phone)
        self.assertEqual(self.supplier.email, new_email)

    def test_update_address(self) -> None:
        address = Address(
            street="500 Pharma Park",
            city="Hyderabad",
            state="Telangana",
            postal_code=PostalCode("500001"),
        )
        self.supplier.update_address(address)
        self.assertEqual(self.supplier.address, address)

    def test_update_compliance_information(self) -> None:
        new_gstin = GSTIN("33ABCDE1234F1Z9")
        new_pan = PAN("XYZDE5678F")
        self.supplier.update_compliance_information(new_gstin, new_pan)
        self.assertEqual(self.supplier.gstin, new_gstin)
        self.assertEqual(self.supplier.pan, new_pan)

    def test_update_supplier_details(self) -> None:
        new_name = SupplierName("Zenith Healthcare Global")
        self.supplier.update_supplier_details(new_name, SupplierCategory.IMPORTER)
        self.assertEqual(self.supplier.name, new_name)
        self.assertEqual(self.supplier.category, SupplierCategory.IMPORTER)
