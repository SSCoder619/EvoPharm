"""Result DTOs for the Sales application use cases.

Read-only Data Transfer Objects returned by application service handlers to represent
the state of Sale aggregates without exposing domain entities or ORM instances.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from ...domain.sales import (
        CustomerReference,
        PrescriptionReference,
        Sale,
        SaleLine,
        SaleTotal,
    )


@dataclass(frozen=True, slots=True)
class CustomerReferenceResult:
    """Read-only result DTO representing customer billing details."""

    customer_id: UUID | None
    name: str | None
    phone: str | None

    @classmethod
    def from_domain(cls, ref: CustomerReference) -> CustomerReferenceResult:
        """Map a CustomerReference value object into a DTO."""
        return cls(
            customer_id=ref.customer_id,
            name=ref.name,
            phone=ref.phone,
        )


@dataclass(frozen=True, slots=True)
class PrescriptionResult:
    """Read-only result DTO representing medical prescription details."""

    prescription_number: str
    doctor_name: str
    doctor_registration_number: str
    prescription_date: date | None

    @classmethod
    def from_domain(cls, ref: PrescriptionReference) -> PrescriptionResult:
        """Map a PrescriptionReference value object into a DTO."""
        return cls(
            prescription_number=ref.prescription_number,
            doctor_name=ref.doctor_name,
            doctor_registration_number=ref.doctor_registration_number,
            prescription_date=ref.prescription_date,
        )


@dataclass(frozen=True, slots=True)
class SaleLineResult:
    """Read-only result DTO representing an item line in a retail sale."""

    line_id: UUID
    medicine_id: UUID
    batch_id: UUID | None
    quantity: int
    returned_quantity: int
    net_quantity: int
    unit_price: Decimal
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    line_total: Decimal
    status: str

    @classmethod
    def from_domain(cls, line: SaleLine) -> SaleLineResult:
        """Map a SaleLine entity into an immutable SaleLineResult DTO."""
        return cls(
            line_id=line.id.value,
            medicine_id=line.medicine_id.value,
            batch_id=line.batch_id.value if line.batch_id else None,
            quantity=line.quantity.value,
            returned_quantity=line.returned_quantity.value,
            net_quantity=line.net_quantity.value,
            unit_price=line.unit_price.value,
            subtotal=line.calculate_subtotal().amount,
            discount_amount=line.calculate_discount_amount().amount,
            tax_amount=line.calculate_tax_amount().amount,
            line_total=line.calculate_line_total().amount,
            status=line.status.value,
        )


@dataclass(frozen=True, slots=True)
class SaleTotalResult:
    """Read-only result DTO representing calculated Sale totals."""

    subtotal: Decimal
    total_discount: Decimal
    taxable_amount: Decimal
    total_tax: Decimal
    net_total: Decimal

    @classmethod
    def from_domain(cls, total: SaleTotal) -> SaleTotalResult:
        """Map a SaleTotal value object into an immutable SaleTotalResult DTO."""
        return cls(
            subtotal=total.subtotal.amount,
            total_discount=total.total_discount.amount,
            taxable_amount=total.taxable_amount.amount,
            total_tax=total.total_tax.amount,
            net_total=total.net_total.amount,
        )


@dataclass(frozen=True, slots=True)
class SaleResult:
    """Read-only result DTO representing a complete Sale aggregate."""

    sale_id: UUID
    customer: CustomerReferenceResult
    invoice_number: str
    prescription: PrescriptionResult | None
    sale_status: str
    payment_status: str
    payment_method: str | None
    total_amount_paid: Decimal
    total: SaleTotalResult
    lines: tuple[SaleLineResult, ...]
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, sale: Sale) -> SaleResult:
        """Map a Sale aggregate root into an immutable SaleResult DTO."""
        return cls(
            sale_id=sale.id.value,
            customer=CustomerReferenceResult.from_domain(sale.customer_reference),
            invoice_number=sale.invoice_number.value,
            prescription=PrescriptionResult.from_domain(sale.prescription_reference) if sale.prescription_reference else None,
            sale_status=sale.sale_status.value,
            payment_status=sale.payment_status.value,
            payment_method=sale.payment_method.value if sale.payment_method else None,
            total_amount_paid=sale.total_amount_paid.amount,
            total=SaleTotalResult.from_domain(sale.calculate_total()),
            lines=tuple(SaleLineResult.from_domain(l) for l in sale.lines),
            version=sale.version,
            created_at=sale.created_at,
            updated_at=sale.updated_at,
        )


@dataclass(frozen=True, slots=True)
class SaleReturnResult:
    """Read-only result DTO representing a customer return transaction result."""

    refund_amount: Decimal
    sale: SaleResult
