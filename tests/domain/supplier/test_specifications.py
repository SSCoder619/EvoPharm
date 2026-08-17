"""Unit tests for Supplier specifications."""
from __future__ import annotations

from unittest import TestCase

from evopharm_retail_erp.domain.supplier import (
    CanDeactivateSupplierSpecification,
    CanPurchaseFromSupplierSpecification,
    GSTIN,
    HasValidTaxRegistrationSpecification,
    IsActiveSupplierSpecification,
    IsInactiveSupplierSpecification,
    IsSuspendedSupplierSpecification,
    PAN,
    PhoneNumber,
    Supplier,
    SupplierName,
)


class SupplierSpecificationsTests(TestCase):
    def setUp(self) -> None:
        self.supplier = Supplier.register(
            name=SupplierName("BioPharma Supply"),
            phone=PhoneNumber("+919123456789"),
            gstin=GSTIN("29ABCDE1234F1Z5"),
            pan=PAN("ABCDE1234F"),
        )

    def test_active_inactive_suspended_specifications(self) -> None:
        spec_active = IsActiveSupplierSpecification()
        spec_inactive = IsInactiveSupplierSpecification()
        spec_suspended = IsSuspendedSupplierSpecification()

        self.assertTrue(spec_active.is_satisfied_by(self.supplier))
        self.assertFalse(spec_inactive.is_satisfied_by(self.supplier))
        self.assertFalse(spec_suspended.is_satisfied_by(self.supplier))

        self.supplier.suspend("Audit hold")
        self.assertFalse(spec_active.is_satisfied_by(self.supplier))
        self.assertTrue(spec_suspended.is_satisfied_by(self.supplier))

    def test_can_purchase_and_can_deactivate(self) -> None:
        spec_purchase = CanPurchaseFromSupplierSpecification()
        spec_deactivate = CanDeactivateSupplierSpecification()

        self.assertTrue(spec_purchase.is_satisfied_by(self.supplier))
        self.assertTrue(spec_deactivate.is_satisfied_by(self.supplier))

    def test_has_valid_tax_registration_specification(self) -> None:
        spec = HasValidTaxRegistrationSpecification()
        self.assertTrue(spec.is_satisfied_by(self.supplier))

        non_compliant = Supplier.register(
            name=SupplierName("Local Chemist"),
            phone=PhoneNumber("+919000000000"),
        )
        self.assertFalse(spec.is_satisfied_by(non_compliant))

    def test_composite_specifications(self) -> None:
        spec_active = IsActiveSupplierSpecification()
        spec_tax = HasValidTaxRegistrationSpecification()

        combined = spec_active & spec_tax
        self.assertTrue(combined.is_satisfied_by(self.supplier))

        inverted = ~spec_active
        self.assertFalse(inverted.is_satisfied_by(self.supplier))
