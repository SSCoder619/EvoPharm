"""Command DTOs for the Invoice application use cases.

Commands are strongly typed, immutable input data transfer objects sent into application service handlers.
They contain no domain logic and have zero dependencies on ORM or web frameworks.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreateInvoiceCommand:
    """Command to initialize a new draft billing invoice."""

    sale_id: UUID | None = None
    sale_invoice_number: str | None = None
    customer_id: UUID | str | None = None
    customer_name: str | None = None
    customer_gstin: str | None = None
    invoice_number: str | None = None
    invoice_type: str = "TAX_INVOICE"
    tax_type: str = "INTRA_STATE"
    invoice_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class AddInvoiceLineCommand:
    """Command to add an item line to a draft invoice."""

    invoice_id: UUID
    medicine_id: UUID
    quantity: int
    unit_price: Decimal | str
    batch_id: UUID | None = None
    discount_percentage: Decimal | str = "0.00"
    tax_rate_percentage: Decimal | str = "0.00"
    line_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class RemoveInvoiceLineCommand:
    """Command to remove a line item from a draft invoice."""

    invoice_id: UUID
    line_id: UUID


@dataclass(frozen=True, slots=True)
class IssueInvoiceCommand:
    """Command to finalize and issue a draft invoice."""

    invoice_id: UUID


@dataclass(frozen=True, slots=True)
class RecordInvoicePaymentCommand:
    """Command to record customer payment settlement against an invoice."""

    invoice_id: UUID
    amount_paid: Decimal | str


@dataclass(frozen=True, slots=True)
class CancelInvoiceCommand:
    """Command to cancel an invoice."""

    invoice_id: UUID
    reason: str
