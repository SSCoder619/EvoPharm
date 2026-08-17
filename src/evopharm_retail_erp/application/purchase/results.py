"""Result DTOs for the Purchase application use cases.

Read-only Data Transfer Objects returned by application service handlers to represent
the state of Purchase aggregates without exposing domain entities or ORM instances.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from ...domain.purchase import Purchase, PurchaseLine, PurchaseTotal


@dataclass(frozen=True, slots=True)
class PurchaseLineResult:
    """Read-only result DTO representing a line item in a Purchase Order."""

    line_id: UUID
    medicine_id: UUID
    ordered_quantity: int
    received_quantity: int
    outstanding_quantity: int
    unit_price: Decimal
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    line_total: Decimal
    status: str

    @classmethod
    def from_domain(cls, line: PurchaseLine) -> PurchaseLineResult:
        """Map a PurchaseLine entity into an immutable PurchaseLineResult DTO."""
        return cls(
            line_id=line.id.value,
            medicine_id=line.medicine_id.value,
            ordered_quantity=line.ordered_quantity.value,
            received_quantity=line.received_quantity.value,
            outstanding_quantity=line.outstanding_quantity.value,
            unit_price=line.unit_price.value,
            subtotal=line.calculate_subtotal().amount,
            discount_amount=line.calculate_discount_amount().amount,
            tax_amount=line.calculate_tax_amount().amount,
            line_total=line.calculate_line_total().amount,
            status=line.status.value,
        )


@dataclass(frozen=True, slots=True)
class PurchaseTotalResult:
    """Read-only result DTO representing calculated Purchase totals."""

    subtotal: Decimal
    total_discount: Decimal
    total_tax: Decimal
    net_total: Decimal

    @classmethod
    def from_domain(cls, total: PurchaseTotal) -> PurchaseTotalResult:
        """Map a PurchaseTotal value object into an immutable PurchaseTotalResult DTO."""
        return cls(
            subtotal=total.subtotal.amount,
            total_discount=total.total_discount.amount,
            total_tax=total.total_tax.amount,
            net_total=total.net_total.amount,
        )


@dataclass(frozen=True, slots=True)
class PurchaseResult:
    """Read-only result DTO representing a complete Purchase Order aggregate."""

    purchase_id: UUID
    supplier_id: UUID | str
    order_reference: str
    invoice_reference: str | None
    purchase_status: str
    receiving_status: str
    payment_status: str
    total_amount_paid: Decimal
    total: PurchaseTotalResult
    lines: tuple[PurchaseLineResult, ...]
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, purchase: Purchase) -> PurchaseResult:
        """Map a Purchase aggregate root into an immutable PurchaseResult DTO."""
        return cls(
            purchase_id=purchase.id.value,
            supplier_id=purchase.supplier_reference.supplier_id,
            order_reference=purchase.order_reference.value,
            invoice_reference=purchase.invoice_reference.value if purchase.invoice_reference else None,
            purchase_status=purchase.purchase_status.value,
            receiving_status=purchase.receiving_status.value,
            payment_status=purchase.payment_status.value,
            total_amount_paid=purchase.total_amount_paid.amount,
            total=PurchaseTotalResult.from_domain(purchase.calculate_total()),
            lines=tuple(PurchaseLineResult.from_domain(l) for l in purchase.lines),
            version=purchase.version,
            created_at=purchase.created_at,
            updated_at=purchase.updated_at,
        )
