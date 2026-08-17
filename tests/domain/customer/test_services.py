"""Unit tests for Customer domain services."""
from __future__ import annotations

from decimal import Decimal
from unittest import TestCase

from evopharm_retail_erp.domain.customer import (
    Customer,
    CustomerEligibilityService,
    CustomerName,
    CustomerType,
    PhoneNumber,
)


class CustomerServicesTests(TestCase):
    def setUp(self) -> None:
        self.service = CustomerEligibilityService(
            senior_citizen_discount_percentage=Decimal("5.00"),
            vip_discount_percentage=Decimal("10.00"),
        )
        self.regular_customer = Customer.register(
            name=CustomerName("Regular Joe"),
            phone=PhoneNumber("+919111111111"),
            customer_type=CustomerType.REGULAR,
        )
        self.senior_customer = Customer.register(
            name=CustomerName("Grandpa Joe"),
            phone=PhoneNumber("+919222222222"),
            customer_type=CustomerType.SENIOR_CITIZEN,
        )
        self.vip_customer = Customer.register(
            name=CustomerName("VIP Victoria"),
            phone=PhoneNumber("+919333333333"),
            customer_type=CustomerType.VIP,
        )

    def test_discount_eligibility_evaluation(self) -> None:
        self.assertEqual(
            self.service.determine_eligible_discount_percentage(self.regular_customer),
            Decimal("0.00"),
        )
        self.assertEqual(
            self.service.determine_eligible_discount_percentage(self.senior_customer),
            Decimal("5.00"),
        )
        self.assertEqual(
            self.service.determine_eligible_discount_percentage(self.vip_customer),
            Decimal("10.00"),
        )

    def test_credit_sale_eligibility(self) -> None:
        self.assertFalse(self.service.is_eligible_for_credit_sale(self.regular_customer))
        self.assertTrue(self.service.is_eligible_for_credit_sale(self.vip_customer))
