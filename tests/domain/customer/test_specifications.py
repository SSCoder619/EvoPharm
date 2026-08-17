"""Unit tests for Customer specifications."""
from __future__ import annotations

from unittest import TestCase

from evopharm_retail_erp.domain.customer import (
    CanDeactivateCustomerSpecification,
    CanUpdateCustomerSpecification,
    Customer,
    CustomerName,
    HasValidContactInformationSpecification,
    IsActiveCustomerSpecification,
    IsInactiveCustomerSpecification,
    PhoneNumber,
)


class CustomerSpecificationsTests(TestCase):
    def setUp(self) -> None:
        self.customer = Customer.register(
            name=CustomerName("Alice Walker"),
            phone=PhoneNumber("+919123456789"),
        )

    def test_active_and_inactive_specifications(self) -> None:
        spec_active = IsActiveCustomerSpecification()
        spec_inactive = IsInactiveCustomerSpecification()

        self.assertTrue(spec_active.is_satisfied_by(self.customer))
        self.assertFalse(spec_inactive.is_satisfied_by(self.customer))

        self.customer.deactivate("Account closed")
        self.assertFalse(spec_active.is_satisfied_by(self.customer))
        self.assertTrue(spec_inactive.is_satisfied_by(self.customer))

    def test_can_update_and_can_deactivate(self) -> None:
        spec_update = CanUpdateCustomerSpecification()
        spec_deactivate = CanDeactivateCustomerSpecification()

        self.assertTrue(spec_update.is_satisfied_by(self.customer))
        self.assertTrue(spec_deactivate.is_satisfied_by(self.customer))

    def test_has_valid_contact_information_specification(self) -> None:
        spec = HasValidContactInformationSpecification()
        self.assertTrue(spec.is_satisfied_by(self.customer))

    def test_composite_specifications(self) -> None:
        spec_active = IsActiveCustomerSpecification()
        spec_update = CanUpdateCustomerSpecification()

        combined = spec_active & spec_update
        self.assertTrue(combined.is_satisfied_by(self.customer))

        inverted = ~spec_active
        self.assertFalse(inverted.is_satisfied_by(self.customer))
