"""Command DTOs for the Sales application use cases.

Commands are strongly typed, immutable input data transfer objects sent into application service handlers.
They contain no domain logic and have zero dependencies on ORM or web frameworks.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreateSaleCommand:
    """Command to initialize a new draft retail sale transaction."""

    customer_id: UUID | str | None = None
    customer_name: str | None = None
    customer_phone: str | None = None
    invoice_number: str | None = None
    prescription_number: str | None = None
    doctor_name: str | None = None
    doctor_registration_number: str | None = None
    sale_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class AddSaleLineCommand:
    """Command to add an item line to a draft retail sale."""

    sale_id: UUID
    medicine_id: UUID
    quantity: int
    unit_price: Decimal | str
    batch_id: UUID | None = None
    discount_percentage: Decimal | str = "0.00"
    tax_rate_percentage: Decimal | str = "0.00"
    line_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class RemoveSaleLineCommand:
    """Command to remove a line item from a draft retail sale."""

    sale_id: UUID
    line_id: UUID


@dataclass(frozen=True, slots=True)
class AttachPrescriptionCommand:
    """Command to attach medical practitioner prescription details to a sale."""

    sale_id: UUID
    prescription_number: str
    doctor_name: str
    doctor_registration_number: str
    prescription_date: date | None = None


@dataclass(frozen=True, slots=True)
class ConfirmSaleCommand:
    """Command to confirm a draft retail sale for billing and stock allocation."""

    sale_id: UUID


@dataclass(frozen=True, slots=True)
class RecordSalePaymentCommand:
    """Command to record customer payment settlement for a sale."""

    sale_id: UUID
    amount_paid: Decimal | str
    payment_method: str = "CASH"
    payment_reference: str | None = None


@dataclass(frozen=True, slots=True)
class CompleteSaleCommand:
    """Command to mark a paid sale as fully completed."""

    sale_id: UUID


@dataclass(frozen=True, slots=True)
class CancelSaleCommand:
    """Command to cancel a retail sale transaction."""

    sale_id: UUID
    reason: str


@dataclass(frozen=True, slots=True)
class ProcessReturnCommand:
    """Command to process a customer return against a sale line."""

    sale_id: UUID
    line_id: UUID
    quantity: int
    reason: str = "CUSTOMER_CHANGED_MIND"
