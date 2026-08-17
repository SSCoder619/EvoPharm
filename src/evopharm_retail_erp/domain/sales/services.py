"""Domain services for the Sales bounded context.

Domain services implement business logic that spans multiple aggregates or represents
a pure domain calculation that does not naturally belong to a single entity.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .entities import Sale
from .value_objects import Discount, Money, SaleTotal


@dataclass(frozen=True, slots=True)
class PromotionalRule:
    """Domain rule for applying promotional volume discounts based on sale subtotal."""

    minimum_subtotal: Money
    discount_percentage: Decimal


@dataclass(frozen=True, slots=True)
class SalesPromotionService:
    """Domain service for evaluating promotional discounts and revenue valuation summaries."""

    rules: tuple[PromotionalRule, ...] = ()

    def calculate_promotional_discount(self, sale: Sale) -> Discount:
        """Evaluate applicable promotional discount for a retail sale based on total subtotal."""
        total = sale.calculate_total()
        subtotal = total.subtotal
        best_discount = Decimal("0.00")

        for rule in self.rules:
            if subtotal >= rule.minimum_subtotal:
                if rule.discount_percentage > best_discount:
                    best_discount = rule.discount_percentage

        return Discount.percent(best_discount)

    def summarize_sales_revenue(
        self, sales: list[Sale] | tuple[Sale, ...]
    ) -> SaleTotal:
        """Calculate aggregate revenue valuation summary across multiple retail sales."""
        if not sales:
            return SaleTotal.zero()

        first_currency = sales[0].calculate_total().subtotal.currency
        total_subtotal = Money.zero(first_currency)
        total_discount = Money.zero(first_currency)
        total_tax = Money.zero(first_currency)

        for sale in sales:
            if sale.sale_status != "CANCELLED":
                s_total = sale.calculate_total()
                total_subtotal = total_subtotal.add(s_total.subtotal)
                total_discount = total_discount.add(s_total.total_discount)
                total_tax = total_tax.add(s_total.total_tax)

        return SaleTotal.create(
            subtotal=total_subtotal,
            total_discount=total_discount,
            total_tax=total_tax,
        )
