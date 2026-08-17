"""Unit tests for Supplier domain services."""
from __future__ import annotations

from unittest import TestCase

from evopharm_retail_erp.domain.supplier import (
    GSTIN,
    PAN,
    PhoneNumber,
    Supplier,
    SupplierCategory,
    SupplierEvaluationService,
    SupplierName,
)


class SupplierServicesTests(TestCase):
    def setUp(self) -> None:
        self.service = SupplierEvaluationService(require_gstin_for_purchases=True)
        self.compliant_supplier = Supplier.register(
            name=SupplierName("Compliant Corp"),
            phone=PhoneNumber("+919111111111"),
            gstin=GSTIN("29ABCDE1234F1Z5"),
            pan=PAN("ABCDE1234F"),
            category=SupplierCategory.MANUFACTURER,
        )
        self.non_compliant_supplier = Supplier.register(
            name=SupplierName("Non Compliant Vendor"),
            phone=PhoneNumber("+919222222222"),
            category=SupplierCategory.WHOLESALER,
        )

    def test_procurement_eligibility(self) -> None:
        self.assertTrue(self.service.is_eligible_for_procurement(self.compliant_supplier))
        self.assertFalse(self.service.is_eligible_for_procurement(self.non_compliant_supplier))

    def test_procurement_risk_categorization(self) -> None:
        self.assertEqual(
            self.service.categorize_procurement_risk(self.compliant_supplier),
            "LOW_RISK_VERIFIED",
        )
        self.assertEqual(
            self.service.categorize_procurement_risk(self.non_compliant_supplier),
            "MEDIUM_RISK_NON_COMPLIANT",
        )

        self.compliant_supplier.suspend("Hold")
        self.assertEqual(
            self.service.categorize_procurement_risk(self.compliant_supplier),
            "HIGH_RISK_SUSPENDED",
        )
