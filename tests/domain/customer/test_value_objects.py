"""Unit tests for Customer domain value objects."""
from __future__ import annotations

from unittest import TestCase
from uuid import UUID

from evopharm_retail_erp.domain.customer import (
    Address,
    CustomerCode,
    CustomerId,
    CustomerName,
    EmailAddress,
    InvalidAddressError,
    InvalidCustomerCodeError,
    InvalidCustomerNameError,
    InvalidEmailAddressError,
    InvalidPhoneNumberError,
    PhoneNumber,
    PostalCode,
)


class CustomerValueObjectsTests(TestCase):
    def test_customer_id_generation_and_string(self) -> None:
        c_id = CustomerId.generate()
        self.assertIsInstance(c_id.value, UUID)
        self.assertEqual(str(c_id), str(c_id.value))

        from_str = CustomerId.from_string(str(c_id.value))
        self.assertEqual(c_id, from_str)

    def test_customer_code_normalization(self) -> None:
        code = CustomerCode("  CUST-2026-0001  ")
        self.assertEqual(code.value, "CUST-2026-0001")
        self.assertEqual(str(code), "CUST-2026-0001")

        with self.assertRaises(InvalidCustomerCodeError):
            CustomerCode("   ")

    def test_customer_name_validation(self) -> None:
        name = CustomerName("  Jane  Doe  ")
        self.assertEqual(name.value, "Jane Doe")
        self.assertEqual(str(name), "Jane Doe")

        with self.assertRaises(InvalidCustomerNameError):
            CustomerName("A")

        with self.assertRaises(InvalidCustomerNameError):
            CustomerName("   ")

    def test_phone_number_formatting(self) -> None:
        phone = PhoneNumber("+91 98765 43210")
        self.assertEqual(phone.value, "+919876543210")
        self.assertEqual(str(phone), "+919876543210")

        with self.assertRaises(InvalidPhoneNumberError):
            PhoneNumber("123")

    def test_email_address_validation(self) -> None:
        email = EmailAddress("  JANE.DOE@example.COM  ")
        self.assertEqual(email.value, "jane.doe@example.com")
        self.assertEqual(str(email), "jane.doe@example.com")

        with self.assertRaises(InvalidEmailAddressError):
            EmailAddress("invalid-email-string")

    def test_postal_code_and_address(self) -> None:
        p_code = PostalCode(" 560001 ")
        self.assertEqual(p_code.value, "560001")

        address = Address(
            street="123 Main Street",
            city="Bengaluru",
            state="Karnataka",
            postal_code=p_code,
        )
        self.assertEqual(address.street, "123 Main Street")
        self.assertEqual(address.city, "Bengaluru")
        self.assertIn("Bengaluru", str(address))

        with self.assertRaises(InvalidAddressError):
            Address(street="", city="City", state="State", postal_code=p_code)
