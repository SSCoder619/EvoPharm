"""Command DTOs for the Purchase application use cases.

Commands are strongly typed, immutable input data transfer objects sent into application service handlers.
They contain no domain logic and have zero dependencies on ORM or web frameworks.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreatePurchaseCommand:
    """Command to initialize a new draft Purchase Order."""

    supplier_id: UUID | str
    order_reference: str | None = None
    purchase_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class AddPurchaseLineCommand:
    """Command to add a line item to a draft Purchase Order."""

    purchase_id: UUID
    medicine_id: UUID
    ordered_quantity: int
    unit_price: Decimal | str
    discount_percentage: Decimal | str = "0.00"
    tax_rate_percentage: Decimal | str = "0.00"
    line_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class RemovePurchaseLineCommand:
    """Command to remove a line item from a draft Purchase Order."""

    purchase_id: UUID
    line_id: UUID


@dataclass(frozen=True, slots=True)
class ApprovePurchaseCommand:
    """Command to approve a draft Purchase Order."""

    purchase_id: UUID
    approved_by_user_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class PlacePurchaseOrderCommand:
    """Command to transmit/place an approved Purchase Order with a supplier."""

    purchase_id: UUID


@dataclass(frozen=True, slots=True)
class ReceivePurchaseStockCommand:
    """Command to record received physical stock against a purchase line."""

    purchase_id: UUID
    line_id: UUID
    quantity: int
    batch_number: str


@dataclass(frozen=True, slots=True)
class CancelPurchaseCommand:
    """Command to cancel a Purchase Order."""

    purchase_id: UUID
    reason: str


@dataclass(frozen=True, slots=True)
class AttachPurchaseInvoiceCommand:
    """Command to attach a commercial supplier invoice reference."""

    purchase_id: UUID
    invoice_number: str


@dataclass(frozen=True, slots=True)
class RecordPurchasePaymentCommand:
    """Command to record a commercial payment against a purchase order."""

    purchase_id: UUID
    amount_paid: Decimal | str
