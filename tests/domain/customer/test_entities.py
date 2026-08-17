"""Unit tests for Customer aggregate root."""
from __future__ import annotations

from unittest import TestCase

from evopharm_retail_erp.domain.customer import (
    Address,
    Customer,
    CustomerAlreadyActiveError,
    CustomerAlreadyInactiveError,
    CustomerName,
    CustomerStatus,
    CustomerType,
    EmailAddress,
    PhoneNumber,
    PostalCode,
)


class CustomerEntitiesTests(TestCase):
    def setUp(self) -> None:
        self.name = CustomerName("John Smith")
        self.phone = PhoneNumber("+919876543210")
        self.email = EmailAddress("john.smith@example.com")
        self.customer = Customer.register(
            name=self.name,
            phone=self.phone,
            email=self.email,
            customer_type=CustomerType.VIP,
        )

    def test_registration_initial_state(self) -> None:
        self.assertEqual(self.customer.name, self.name)
        self.assertEqual(self.customer.phone, self.phone)
        self.assertEqual(self.customer.email, self.email)
        self.assertEqual(self.customer.status, CustomerStatus.ACTIVE)
        self.assertEqual(self.customer.customer_type, CustomerType.VIP)
        self.assertTrue(self.customer.is_active)

    def test_lifecycle_deactivate_and_activate(self) -> None:
        self.customer.deactivate("Customer requested opt-out")
        self.assertEqual(self.customer.status, CustomerStatus.INACTIVE)
        self.assertFalse(self.customer.is_active)

        with self.assertRaises(CustomerAlreadyInactiveError):
            self.customer.deactivate("Double deactivate")

        self.customer.activate("Re-subscribed")
        self.assertEqual(self.customer.status, CustomerStatus.ACTIVE)

        with self.assertRaises(CustomerAlreadyActiveError):
            self.customer.activate()

    def test_suspend_account(self) -> None:
        self.customer.suspend("Payment dispute")
        self.assertEqual(self.customer.status, CustomerStatus.SUSPENDED)

    def test_update_contact_information(self) -> None:
        new_phone = PhoneNumber("+919988776655")
        new_email = EmailAddress("new.john@example.com")

        self.customer.update_contact_information(new_phone, new_email)
        self.assertEqual(self.customer.phone, new_phone)
        self.assertEqual(self.customer.email, new_email)

    def test_update_address(self) -> None:
        address = Address(
            street="456 Park Avenue",
            city="Mumbai",
            state="Maharashtra",
            postal_code=PostalCode("400001"),
        )
        self.customer.update_address(address)
        self.assertEqual(self.customer.address, address)

    def test_update_profile(self) -> None:
        new_name = CustomerName("Jonathan Smith")
        self.customer.update_profile(new_name, CustomerType.SENIOR_CITIZEN)
        self.assertEqual(self.customer.name, new_name)
        self.assertEqual(self.customer.customer_type, CustomerType.SENIOR_CITIZEN)
