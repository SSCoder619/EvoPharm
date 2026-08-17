"""Unit tests for Customer domain enums."""
from __future__ import annotations

from unittest import TestCase

from evopharm_retail_erp.domain.customer import CustomerStatus, CustomerType


class CustomerEnumsTests(TestCase):
    def test_customer_status_enum_values(self) -> None:
        self.assertEqual(CustomerStatus.ACTIVE.value, "ACTIVE")
        self.assertEqual(CustomerStatus.INACTIVE.value, "INACTIVE")
        self.assertEqual(CustomerStatus.SUSPENDED.value, "SUSPENDED")
        self.assertEqual(CustomerStatus.ARCHIVED.value, "ARCHIVED")

    def test_customer_type_enum_values(self) -> None:
        self.assertEqual(CustomerType.REGULAR.value, "REGULAR")
        self.assertEqual(CustomerType.VIP.value, "VIP")
        self.assertEqual(CustomerType.SENIOR_CITIZEN.value, "SENIOR_CITIZEN")
        self.assertEqual(CustomerType.CORPORATE.value, "CORPORATE")
