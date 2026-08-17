"""Domain services for the Purchase bounded context.

Domain services implement business logic that spans multiple aggregates or represents
a pure domain calculation that does not naturally belong to a single entity.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .entities import Purchase
from .value_objects import Discount, Money, PurchaseTotal


@dataclass(frozen=True, slots=True)
class VolumeDiscountRule:
    """Domain rule for applying bulk volume discount based on total purchase subtotal."""

    minimum_subtotal: Money
    discount_percentage: Decimal


@dataclass(frozen=True, slots=True)
class PurchasePricingService:
    """Domain service for evaluating volume discounts and total procurement valuation."""

    volume_rules: tuple[VolumeDiscountRule, ...] = ()

    def calculate_volume_discount(self, purchase: Purchase) -> Discount:
        """Evaluate applicable volume discount for a purchase order based on total subtotal."""
        total = purchase.calculate_total()
        subtotal = total.subtotal
        best_discount = Decimal("0.00")

        for rule in self.volume_rules:
            if subtotal >= rule.minimum_subtotal:
                if rule.discount_percentage > best_discount:
                    best_discount = rule.discount_percentage

        return Discount.percent(best_discount)

    def summarize_procurement_valuation(
        self, purchases: list[Purchase] | tuple[Purchase, ...]
    ) -> PurchaseTotal:
        """Calculate aggregate financial valuation summary across multiple purchase orders."""
        if not purchases:
            return PurchaseTotal.zero()

        first_currency = purchases[0].calculate_total().subtotal.currency
        total_subtotal = Money.zero(first_currency)
        total_discount = Money.zero(first_currency)
        total_tax = Money.zero(first_currency)

        for purchase in purchases:
            p_total = purchase.calculate_total()
            total_subtotal = total_subtotal.add(p_total.subtotal)
            total_discount = total_discount.add(p_total.total_discount)
            total_tax = total_tax.add(p_total.total_tax)

        return PurchaseTotal.create(
            subtotal=total_subtotal,
            total_discount=total_discount,
            total_tax=total_tax,
        )
