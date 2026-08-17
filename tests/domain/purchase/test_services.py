"""Unit tests for Purchase domain services."""
from __future__ import annotations

from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.domain.medicine import MedicineId
from evopharm_retail_erp.domain.purchase import (
    Money,
    Purchase,
    PurchaseOrderReference,
    PurchasePricingService,
    PurchaseQuantity,
    SupplierReference,
    UnitPrice,
    VolumeDiscountRule,
)


class PurchaseServicesTests(TestCase):
    def setUp(self) -> None:
        self.supplier_ref = SupplierReference.of(uuid4())
        self.pricing_service = PurchasePricingService(
            volume_rules=(
                VolumeDiscountRule(
                    minimum_subtotal=Money.of("5000.00"),
                    discount_percentage=Decimal("5.00"),
                ),
                VolumeDiscountRule(
                    minimum_subtotal=Money.of("10000.00"),
                    discount_percentage=Decimal("10.00"),
                ),
            )
        )

    def test_volume_discount_evaluation(self) -> None:
        p = Purchase.create(self.supplier_ref, PurchaseOrderReference("PO-VOL-1"))
        p.add_line(
            medicine_id=MedicineId.generate(),
            ordered_quantity=PurchaseQuantity(60),
            unit_price=UnitPrice.of("100.00"),  # 6000.00 subtotal -> 5% discount
        )

        disc = self.pricing_service.calculate_volume_discount(p)
        self.assertEqual(disc.percentage, Decimal("5.00"))

    def test_summarize_procurement_valuation(self) -> None:
        p1 = Purchase.create(self.supplier_ref, PurchaseOrderReference("PO-VAL-1"))
        p1.add_line(
            medicine_id=MedicineId.generate(),
            ordered_quantity=PurchaseQuantity(10),
            unit_price=UnitPrice.of("100.00"),  # 1000.00
        )

        p2 = Purchase.create(self.supplier_ref, PurchaseOrderReference("PO-VAL-2"))
        p2.add_line(
            medicine_id=MedicineId.generate(),
            ordered_quantity=PurchaseQuantity(20),
            unit_price=UnitPrice.of("50.00"),  # 1000.00
        )

        valuation = self.pricing_service.summarize_procurement_valuation([p1, p2])
        self.assertEqual(valuation.subtotal.amount, Decimal("2000.00"))
        self.assertEqual(valuation.net_total.amount, Decimal("2000.00"))
