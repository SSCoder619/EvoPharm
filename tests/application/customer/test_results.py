"""Unit tests for Customer result DTOs."""
from __future__ import annotations

from unittest import TestCase

from evopharm_retail_erp.application.customer import CustomerResult
from evopharm_retail_erp.domain.customer import (
    Address,
    Customer,
    CustomerCode,
    CustomerName,
    CustomerType,
    EmailAddress,
    PhoneNumber,
    PostalCode,
)


class CustomerResultsTests(TestCase):
    def test_customer_result_mapping_from_domain(self) -> None:
        customer = Customer.register(
            name=CustomerName("Bob Builder"),
            phone=PhoneNumber("9876543210"),
            code=CustomerCode("CUST-99999"),
            email=EmailAddress("bob@builder.com"),
            address=Address(
                street="789 Industrial Rd",
                city="Nagpur",
                state="Maharashtra",
                postal_code=PostalCode("440001"),
            ),
            customer_type=CustomerType.VIP,
        )

        res = CustomerResult.from_domain(customer)

        self.assertEqual(res.customer_id, customer.id.value)
        self.assertEqual(res.code, "CUST-99999")
        self.assertEqual(res.name, "Bob Builder")
        self.assertEqual(res.phone, "9876543210")
        self.assertEqual(res.email, "bob@builder.com")
        self.assertIsNotNone(res.address)
        self.assertEqual(res.address.city, "Nagpur")
        self.assertEqual(res.address.pincode, "440001")
        self.assertEqual(res.status, "ACTIVE")
        self.assertEqual(res.customer_type, "VIP")
