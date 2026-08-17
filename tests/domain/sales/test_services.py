"""Unit tests for Sales domain services."""
from __future__ import annotations

from decimal import Decimal
from unittest import TestCase

from evopharm_retail_erp.domain.medicine import MedicineId
from evopharm_retail_erp.domain.sales import (
    Money,
    PromotionalRule,
    Sale,
    SaleQuantity,
    SalesPromotionService,
    UnitPrice,
)


class SalesServicesTests(TestCase):
    def setUp(self) -> None:
        self.promotion_service = SalesPromotionService(
            rules=(
                PromotionalRule(
                    minimum_subtotal=Money.of("1000.00"),
                    discount_percentage=Decimal("5.00"),
                ),
                PromotionalRule(
                    minimum_subtotal=Money.of("5000.00"),
                    discount_percentage=Decimal("10.00"),
                ),
            )
        )

    def test_promotional_discount_evaluation(self) -> None:
        s = Sale.create()
        s.add_line(
            medicine_id=MedicineId.generate(),
            quantity=SaleQuantity(20),
            unit_price=UnitPrice.of("100.00"),  # 2000.00 subtotal -> 5% discount
        )

        disc = self.promotion_service.calculate_promotional_discount(s)
        self.assertEqual(disc.percentage, Decimal("5.00"))

    def test_summarize_sales_revenue(self) -> None:
        s1 = Sale.create()
        s1.add_line(
            medicine_id=MedicineId.generate(),
            quantity=SaleQuantity(10),
            unit_price=UnitPrice.of("50.00"),  # 500.00
        )

        s2 = Sale.create()
        s2.add_line(
            medicine_id=MedicineId.generate(),
            quantity=SaleQuantity(5),
            unit_price=UnitPrice.of("100.00"),  # 500.00
        )

        revenue_summary = self.promotion_service.summarize_sales_revenue([s1, s2])
        self.assertEqual(revenue_summary.subtotal.amount, Decimal("1000.00"))
        self.assertEqual(revenue_summary.net_total.amount, Decimal("1000.00"))
