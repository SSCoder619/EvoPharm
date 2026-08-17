"""Result DTOs for the Invoice application use cases.

Read-only Data Transfer Objects returned by application service handlers to represent
the state of Invoice aggregates without exposing domain entities or ORM instances.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from ...domain.invoice import (
        CustomerReference,
        GstBreakdown,
        Invoice,
        InvoiceLine,
        InvoiceTotal,
        SaleReference,
    )


@dataclass(frozen=True, slots=True)
class CustomerReferenceResult:
    """Read-only result DTO representing invoice customer reference information."""

    customer_id: UUID | None
    name: str | None
    gstin: str | None

    @classmethod
    def from_domain(cls, ref: CustomerReference) -> CustomerReferenceResult:
        """Map a CustomerReference value object into a DTO."""
        return cls(
            customer_id=ref.customer_id,
            name=ref.name,
            gstin=ref.gstin,
        )


@dataclass(frozen=True, slots=True)
class SaleReferenceResult:
    """Read-only result DTO representing a source retail Sale transaction reference."""

    sale_id: UUID
    sale_invoice_number: str | None

    @classmethod
    def from_domain(cls, ref: SaleReference) -> SaleReferenceResult:
        """Map a SaleReference value object into a DTO."""
        return cls(
            sale_id=ref.sale_id,
            sale_invoice_number=ref.sale_invoice_number,
        )


@dataclass(frozen=True, slots=True)
class GstBreakdownResult:
    """Read-only result DTO representing explicit Indian GST tax breakdown."""

    tax_type: str
    total_tax: Decimal
    cgst: Decimal
    sgst: Decimal
    igst: Decimal

    @classmethod
    def from_domain(cls, breakdown: GstBreakdown) -> GstBreakdownResult:
        """Map a GstBreakdown value object into a DTO."""
        return cls(
            tax_type=breakdown.tax_type.value,
            total_tax=breakdown.total_tax.amount,
            cgst=breakdown.cgst.amount,
            sgst=breakdown.sgst.amount,
            igst=breakdown.igst.amount,
        )


@dataclass(frozen=True, slots=True)
class InvoiceLineResult:
    """Read-only result DTO representing an item line in a billing invoice."""

    line_id: UUID
    medicine_id: UUID
    batch_id: UUID | None
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
    discount_amount: Decimal
    taxable_amount: Decimal
    gst_breakdown: GstBreakdownResult
    line_total: Decimal
    status: str

    @classmethod
    def from_domain(cls, line: InvoiceLine) -> InvoiceLineResult:
        """Map an InvoiceLine entity into an immutable InvoiceLineResult DTO."""
        return cls(
            line_id=line.id.value,
            medicine_id=line.medicine_id.value,
            batch_id=line.batch_id.value if line.batch_id else None,
            quantity=line.quantity.value,
            unit_price=line.unit_price.value,
            subtotal=line.calculate_subtotal().amount,
            discount_amount=line.calculate_discount_amount().amount,
            taxable_amount=line.calculate_taxable_amount().amount,
            gst_breakdown=GstBreakdownResult.from_domain(line.calculate_gst_breakdown()),
            line_total=line.calculate_line_total().amount,
            status=line.status.value,
        )


@dataclass(frozen=True, slots=True)
class InvoiceTotalResult:
    """Read-only result DTO representing calculated Invoice totals."""

    subtotal: Decimal
    total_discount: Decimal
    taxable_amount: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    total_tax: Decimal
    net_total: Decimal

    @classmethod
    def from_domain(cls, total: InvoiceTotal) -> InvoiceTotalResult:
        """Map an InvoiceTotal value object into an immutable InvoiceTotalResult DTO."""
        return cls(
            subtotal=total.subtotal.amount,
            total_discount=total.total_discount.amount,
            taxable_amount=total.taxable_amount.amount,
            cgst_amount=total.cgst_amount.amount,
            sgst_amount=total.sgst_amount.amount,
            igst_amount=total.igst_amount.amount,
            total_tax=total.total_tax.amount,
            net_total=total.net_total.amount,
        )


@dataclass(frozen=True, slots=True)
class InvoiceResult:
    """Read-only result DTO representing a complete Invoice aggregate."""

    invoice_id: UUID
    number: str
    sale_reference: SaleReferenceResult | None
    customer: CustomerReferenceResult | None
    invoice_type: str
    tax_type: str
    status: str
    payment_status: str
    total_amount_paid: Decimal
    total: InvoiceTotalResult
    lines: tuple[InvoiceLineResult, ...]
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, invoice: Invoice) -> InvoiceResult:
        """Map an Invoice aggregate root into an immutable InvoiceResult DTO."""
        return cls(
            invoice_id=invoice.id.value,
            number=invoice.number.value,
            sale_reference=SaleReferenceResult.from_domain(invoice.sale_reference) if invoice.sale_reference else None,
            customer=CustomerReferenceResult.from_domain(invoice.customer_reference) if invoice.customer_reference else None,
            invoice_type=invoice.invoice_type.value,
            tax_type=invoice.tax_type.value,
            status=invoice.status.value,
            payment_status=invoice.payment_status.value,
            total_amount_paid=invoice.total_amount_paid.amount,
            total=InvoiceTotalResult.from_domain(invoice.calculate_total()),
            lines=tuple(InvoiceLineResult.from_domain(l) for l in invoice.lines),
            version=invoice.version,
            created_at=invoice.created_at,
            updated_at=invoice.updated_at,
        )
