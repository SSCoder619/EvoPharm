"""Domain services for the Customer bounded context.

Domain services implement business logic that spans multiple aggregates or represents
a pure domain calculation that does not naturally belong to a single entity.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .entities import Customer
from .enums import CustomerStatus, CustomerType


@dataclass(frozen=True, slots=True)
class CustomerEligibilityService:
    """Domain service for evaluating customer discount tiering and special privileges."""

    senior_citizen_discount_percentage: Decimal = Decimal("5.00")
    vip_discount_percentage: Decimal = Decimal("10.00")

    def determine_eligible_discount_percentage(self, customer: Customer) -> Decimal:
        """Determine eligible percentage discount based on customer status and customer type."""
        if customer.status != CustomerStatus.ACTIVE:
            return Decimal("0.00")

        if customer.customer_type == CustomerType.VIP:
            return self.vip_discount_percentage
        elif customer.customer_type == CustomerType.SENIOR_CITIZEN:
            return self.senior_citizen_discount_percentage

        return Decimal("0.00")

    def is_eligible_for_credit_sale(self, customer: Customer) -> bool:
        """Evaluate whether a customer is eligible for credit billing sales."""
        return customer.status == CustomerStatus.ACTIVE and customer.customer_type in (
            CustomerType.VIP,
            CustomerType.CORPORATE,
        )
