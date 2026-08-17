"""Domain services for the Invoice bounded context.

Domain services implement business logic that spans multiple aggregates or represents
a pure domain calculation that does not naturally belong to a single entity.
"""
from __future__ import annotations

from dataclasses import dataclass

from .entities import Invoice
from .enums import InvoiceStatus
from .value_objects import InvoiceTotal, Money


@dataclass(frozen=True, slots=True)
class InvoiceTaxCalculationService:
    """Domain service for calculating aggregate GST tax liabilities across invoices."""

    def summarize_tax_liabilities(
        self, invoices: list[Invoice] | tuple[Invoice, ...]
    ) -> InvoiceTotal:
        """Calculate aggregate subtotal, discounts, CGST, SGST, IGST, and net totals across multiple invoices."""
        if not invoices:
            return InvoiceTotal.zero()

        first_currency = invoices[0].calculate_total().subtotal.currency
        subtotal = Money.zero(first_currency)
        total_discount = Money.zero(first_currency)
        cgst_amount = Money.zero(first_currency)
        sgst_amount = Money.zero(first_currency)
        igst_amount = Money.zero(first_currency)

        for inv in invoices:
            if inv.status not in (InvoiceStatus.CANCELLED, InvoiceStatus.VOID):
                t = inv.calculate_total()
                subtotal = subtotal.add(t.subtotal)
                total_discount = total_discount.add(t.total_discount)
                cgst_amount = cgst_amount.add(t.cgst_amount)
                sgst_amount = sgst_amount.add(t.sgst_amount)
                igst_amount = igst_amount.add(t.igst_amount)

        return InvoiceTotal.create(
            subtotal=subtotal,
            total_discount=total_discount,
            cgst_amount=cgst_amount,
            sgst_amount=sgst_amount,
            igst_amount=igst_amount,
        )
