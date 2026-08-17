"""Unit tests for Supplier domain value objects."""
from __future__ import annotations

from unittest import TestCase
from uuid import UUID

from evopharm_retail_erp.domain.supplier import (
    GSTIN,
    PAN,
    Address,
    EmailAddress,
    InvalidAddressError,
    InvalidEmailAddressError,
    InvalidGSTINError,
    InvalidPANError,
    InvalidPhoneNumberError,
    InvalidSupplierCodeError,
    InvalidSupplierNameError,
    PhoneNumber,
    PostalCode,
    SupplierCode,
    SupplierId,
    SupplierName,
)


class SupplierValueObjectsTests(TestCase):
    def test_supplier_id_generation_and_string(self) -> None:
        s_id = SupplierId.generate()
        self.assertIsInstance(s_id.value, UUID)
        self.assertEqual(str(s_id), str(s_id.value))

        from_str = SupplierId.from_string(str(s_id.value))
        self.assertEqual(s_id, from_str)

    def test_supplier_code_normalization(self) -> None:
        code = SupplierCode("  SUP-2026-0001  ")
        self.assertEqual(code.value, "SUP-2026-0001")
        self.assertEqual(str(code), "SUP-2026-0001")

        with self.assertRaises(InvalidSupplierCodeError):
            SupplierCode("   ")

    def test_supplier_name_validation(self) -> None:
        name = SupplierName("  Apex  Pharma  Ltd  ")
        self.assertEqual(name.value, "Apex Pharma Ltd")
        self.assertEqual(str(name), "Apex Pharma Ltd")

        with self.assertRaises(InvalidSupplierNameError):
            SupplierName("A")

        with self.assertRaises(InvalidSupplierNameError):
            SupplierName("   ")

    def test_phone_number_formatting(self) -> None:
        phone = PhoneNumber("+91 98765 43210")
        self.assertEqual(phone.value, "+919876543210")

        with self.assertRaises(InvalidPhoneNumberError):
            PhoneNumber("123")

    def test_email_address_validation(self) -> None:
        email = EmailAddress("  ORDERS@APEXPHARMA.COM  ")
        self.assertEqual(email.value, "orders@apexpharma.com")

        with self.assertRaises(InvalidEmailAddressError):
            EmailAddress("invalid-email-string")

    def test_gstin_validation(self) -> None:
        gstin = GSTIN("29ABCDE1234F1Z5")
        self.assertEqual(gstin.value, "29ABCDE1234F1Z5")
        self.assertEqual(str(gstin), "29ABCDE1234F1Z5")

        with self.assertRaises(InvalidGSTINError):
            GSTIN("INVALIDGSTIN123")

    def test_pan_validation(self) -> None:
        pan = PAN("ABCDE1234F")
        self.assertEqual(pan.value, "ABCDE1234F")
        self.assertEqual(str(pan), "ABCDE1234F")

        with self.assertRaises(InvalidPANError):
            PAN("INVALIDPAN")

    def test_postal_code_and_address(self) -> None:
        p_code = PostalCode(" 400001 ")
        self.assertEqual(p_code.value, "400001")

        address = Address(
            street="100 Industrial Estate",
            city="Mumbai",
            state="Maharashtra",
            postal_code=p_code,
        )
        self.assertEqual(address.street, "100 Industrial Estate")
        self.assertEqual(address.city, "Mumbai")
        self.assertIn("Mumbai", str(address))

        with self.assertRaises(InvalidAddressError):
            Address(street="", city="City", state="State", postal_code=p_code)
