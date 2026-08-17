"""Unit tests for Invoice specifications."""
from __future__ import annotations

from unittest import TestCase

from evopharm_retail_erp.domain.invoice import (
    CanCancelInvoiceSpecification,
    CanIssueInvoiceSpecification,
    HasOutstandingBalanceSpecification,
    Invoice,
    InvoiceQuantity,
    IsCancelledInvoiceSpecification,
    IsDraftInvoiceSpecification,
    IsIssuedInvoiceSpecification,
    IsPaidInvoiceSpecification,
    Money,
    UnitPrice,
)
from evopharm_retail_erp.domain.medicine import MedicineId


class InvoiceSpecificationsTests(TestCase):
    def setUp(self) -> None:
        self.invoice = Invoice.create()
        self.med_id = MedicineId.generate()

    def test_draft_issued_paid_specifications(self) -> None:
        spec_draft = IsDraftInvoiceSpecification()
        spec_issued = IsIssuedInvoiceSpecification()
        spec_paid = IsPaidInvoiceSpecification()

        self.assertTrue(spec_draft.is_satisfied_by(self.invoice))
        self.assertFalse(spec_issued.is_satisfied_by(self.invoice))
        self.assertFalse(spec_paid.is_satisfied_by(self.invoice))

        self.invoice.add_line(
            medicine_id=self.med_id,
            quantity=InvoiceQuantity(1),
            unit_price=UnitPrice.of("100.00"),
        )
        self.invoice.issue()
        self.assertFalse(spec_draft.is_satisfied_by(self.invoice))
        self.assertTrue(spec_issued.is_satisfied_by(self.invoice))

        self.invoice.record_payment(Money.of("100.00"))
        self.assertTrue(spec_paid.is_satisfied_by(self.invoice))

    def test_can_issue_and_can_cancel(self) -> None:
        spec_can_issue = CanIssueInvoiceSpecification()
        spec_can_cancel = CanCancelInvoiceSpecification()

        # Cannot issue empty invoice
        self.assertFalse(spec_can_issue.is_satisfied_by(self.invoice))
        self.assertTrue(spec_can_cancel.is_satisfied_by(self.invoice))

        self.invoice.add_line(
            medicine_id=self.med_id,
            quantity=InvoiceQuantity(1),
            unit_price=UnitPrice.of("50.00"),
        )
        self.assertTrue(spec_can_issue.is_satisfied_by(self.invoice))

    def test_composite_specifications(self) -> None:
        spec_draft = IsDraftInvoiceSpecification()
        spec_outstanding = HasOutstandingBalanceSpecification()

        combined = spec_draft & spec_outstanding
        self.assertTrue(combined.is_satisfied_by(self.invoice))

        inverted = ~spec_draft
        self.assertFalse(inverted.is_satisfied_by(self.invoice))
