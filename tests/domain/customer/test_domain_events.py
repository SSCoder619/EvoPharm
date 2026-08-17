"""Unit tests for Customer domain events."""
from __future__ import annotations

from unittest import TestCase

from evopharm_retail_erp.domain.customer import (
    Address,
    Customer,
    CustomerActivated,
    CustomerAddressUpdated,
    CustomerContactUpdated,
    CustomerDeactivated,
    CustomerName,
    CustomerProfileUpdated,
    CustomerRegistered,
    CustomerSuspended,
    CustomerType,
    EmailAddress,
    PhoneNumber,
    PostalCode,
)


class CustomerDomainEventsTests(TestCase):
    def test_customer_events_emission(self) -> None:
        # 1. CustomerRegistered
        customer = Customer.register(
            name=CustomerName("Bob Brown"),
            phone=PhoneNumber("+919000000001"),
        )
        self.assertEqual(len(customer.events), 1)
        self.assertIsInstance(customer.events[0], CustomerRegistered)

        # 2. CustomerContactUpdated
        new_phone = PhoneNumber("+919000000002")
        customer.update_contact_information(new_phone, EmailAddress("bob@example.com"))
        self.assertEqual(len(customer.events), 2)
        self.assertIsInstance(customer.events[1], CustomerContactUpdated)

        # 3. CustomerAddressUpdated
        addr = Address("789 Road", "Delhi", "Delhi", PostalCode("110001"))
        customer.update_address(addr)
        self.assertEqual(len(customer.events), 3)
        self.assertIsInstance(customer.events[2], CustomerAddressUpdated)

        # 4. CustomerProfileUpdated
        customer.update_profile(CustomerName("Robert Brown"), CustomerType.VIP)
        self.assertEqual(len(customer.events), 4)
        self.assertIsInstance(customer.events[3], CustomerProfileUpdated)

        # 5. CustomerDeactivated & CustomerActivated
        customer.deactivate("Temporary pause")
        self.assertIsInstance(customer.events[4], CustomerDeactivated)

        customer.activate()
        self.assertIsInstance(customer.events[5], CustomerActivated)

        # 6. CustomerSuspended
        customer.suspend("Compliance issue")
        self.assertIsInstance(customer.events[6], CustomerSuspended)
