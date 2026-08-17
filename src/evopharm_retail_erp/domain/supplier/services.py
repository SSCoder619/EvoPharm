"""Domain services for the Supplier bounded context.

Domain services implement business logic that spans multiple aggregates or represents
a pure domain calculation that does not naturally belong to a single entity.
"""
from __future__ import annotations

from dataclasses import dataclass

from .entities import Supplier
from .enums import SupplierStatus, SupplierCategory


@dataclass(frozen=True, slots=True)
class SupplierEvaluationService:
    """Domain service for evaluating supplier tax compliance readiness and procurement eligibility."""

    require_gstin_for_purchases: bool = True

    def is_eligible_for_procurement(self, supplier: Supplier) -> bool:
        """Evaluate whether a supplier is eligible to receive procurement purchase orders."""
        if supplier.status != SupplierStatus.ACTIVE:
            return False

        if self.require_gstin_for_purchases and supplier.gstin is None:
            return False

        return True

    def categorize_procurement_risk(self, supplier: Supplier) -> str:
        """Categorize supplier procurement risk based on status, compliance, and category."""
        if supplier.status == SupplierStatus.SUSPENDED:
            return "HIGH_RISK_SUSPENDED"

        if supplier.status == SupplierStatus.INACTIVE:
            return "INACTIVE"

        if not supplier.is_tax_compliant:
            return "MEDIUM_RISK_NON_COMPLIANT"

        if supplier.category in (SupplierCategory.MANUFACTURER, SupplierCategory.DISTRIBUTOR):
            return "LOW_RISK_VERIFIED"

        return "LOW_RISK_STANDARD"
