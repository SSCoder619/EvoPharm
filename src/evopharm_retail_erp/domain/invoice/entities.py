"""Entities for the Invoice bounded context.

Following DDD principles, Invoice is the Aggregate Root representing a billing
document transaction. InvoiceLine is a child entity belonging exclusively to an Invoice aggregate.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

from ..medicine.value_objects import MedicineBatchId, MedicineId
from .domain_events import (
    InvoiceCancelled,
    InvoiceCreated,
    InvoiceDomainEvent,
    InvoiceIssued,
    InvoiceLineAdded,
    InvoiceLineRemoved,
    InvoicePaid,
    InvoicePartiallyPaid,
    InvoicePaymentRecorded,
)
from .enums import (
    InvoiceLineStatus,
    InvoiceStatus,
    InvoiceType,
    PaymentStatus,
    TaxType,
)
from .exceptions import (
    DuplicateInvoiceLineError,
    InvalidInvoiceLineError,
    InvalidInvoiceQuantityError,
    InvalidInvoiceStateError,
    InvalidPaymentStateError,
    InvoiceAlreadyCancelledError,
    InvoiceLineNotFoundError,
    InvoiceNotCancellableError,
    OverpaymentError,
)
from .value_objects import (
    CustomerReference,
    DiscountAmount,
    GstBreakdown,
    InvoiceId,
    InvoiceLineId,
    InvoiceNumber,
    InvoiceQuantity,
    InvoiceTotal,
    Money,
    SaleReference,
    TaxRate,
    UnitPrice,
)


@dataclass(slots=True, eq=False)
class InvoiceLine:
    """Child entity representing an individual item line in a billing invoice."""

    id: InvoiceLineId
    medicine_id: MedicineId
    quantity: InvoiceQuantity
    unit_price: UnitPrice
    batch_id: MedicineBatchId | None = None
    discount: DiscountAmount = field(default_factory=DiscountAmount.none)
    tax_rate: TaxRate = field(default_factory=TaxRate.zero)
    tax_type: TaxType = TaxType.INTRA_STATE
    status: InvoiceLineStatus = InvoiceLineStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, InvoiceLine):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def is_cancelled(self) -> bool:
        return self.status == InvoiceLineStatus.CANCELLED

    # -- Monetary & Tax Calculations ------------------------------------

    def calculate_subtotal(self) -> Money:
        """Raw subtotal before discount and tax."""
        return self.unit_price.multiply(self.quantity)

    def calculate_discount_amount(self) -> Money:
        """Monetary discount amount for this line."""
        subtotal = self.calculate_subtotal()
        return self.discount.calculate_discount_amount(subtotal)

    def calculate_taxable_amount(self) -> Money:
        """Taxable base amount after discount."""
        subtotal = self.calculate_subtotal()
        disc = self.calculate_discount_amount()
        if disc >= subtotal:
            return Money.zero(subtotal.currency)
        return subtotal.subtract(disc)

    def calculate_gst_breakdown(self) -> GstBreakdown:
        """Calculate detailed CGST, SGST, IGST breakdown for this line."""
        taxable = self.calculate_taxable_amount()
        return GstBreakdown.calculate(
            taxable_amount=taxable,
            tax_rate=self.tax_rate,
            tax_type=self.tax_type,
        )

    def calculate_line_total(self) -> Money:
        """Final net total for this line (taxable + total_tax)."""
        taxable = self.calculate_taxable_amount()
        breakdown = self.calculate_gst_breakdown()
        return taxable.add(breakdown.total_tax)

    # -- State Mutations ------------------------------------------------

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    def cancel(self) -> None:
        """Cancel this line item."""
        self.status = InvoiceLineStatus.CANCELLED
        self._touch()


@dataclass(slots=True, eq=False)
class Invoice:
    """Aggregate Root representing a commercial billing invoice transaction."""

    id: InvoiceId
    number: InvoiceNumber
    sale_reference: SaleReference | None = None
    customer_reference: CustomerReference | None = None
    invoice_type: InvoiceType = InvoiceType.TAX_INVOICE
    tax_type: TaxType = TaxType.INTRA_STATE
    status: InvoiceStatus = InvoiceStatus.DRAFT
    payment_status: PaymentStatus = PaymentStatus.UNPAID
    total_amount_paid: Money = field(default_factory=Money.zero)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1
    _lines: dict[UUID, InvoiceLine] = field(default_factory=dict)
    _events: list[InvoiceDomainEvent] = field(default_factory=list)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Invoice):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    # -- Factory --------------------------------------------------------

    @classmethod
    def create(
        cls,
        number: InvoiceNumber | None = None,
        sale_reference: SaleReference | None = None,
        customer_reference: CustomerReference | None = None,
        invoice_type: InvoiceType = InvoiceType.TAX_INVOICE,
        tax_type: TaxType = TaxType.INTRA_STATE,
        id: InvoiceId | None = None,
    ) -> "Invoice":
        """Initialize a new retail Invoice aggregate root."""
        i_id = id if id is not None else InvoiceId.generate()
        inv_num = number if number is not None else InvoiceNumber(f"INV-{i_id.value.hex[:8].upper()}")
        now = datetime.now(timezone.utc)

        invoice = cls(
            id=i_id,
            number=inv_num,
            sale_reference=sale_reference,
            customer_reference=customer_reference,
            invoice_type=invoice_type,
            tax_type=tax_type,
            status=InvoiceStatus.DRAFT,
            payment_status=PaymentStatus.UNPAID,
            created_at=now,
            updated_at=now,
        )
        invoice._record_event(
            InvoiceCreated(
                invoice_id=i_id,
                number=inv_num,
                sale_reference=sale_reference,
                customer_reference=customer_reference,
            )
        )
        return invoice

    # -- Properties & Views ---------------------------------------------

    @property
    def lines(self) -> tuple[InvoiceLine, ...]:
        """Read-only tuple of line items in this invoice."""
        return tuple(self._lines.values())

    @property
    def events(self) -> tuple[InvoiceDomainEvent, ...]:
        """Read-only tuple of uncommitted domain events emitted by this aggregate."""
        return tuple(self._events)

    def clear_events(self) -> None:
        """Clear all domain events after dispatch."""
        self._events.clear()

    # -- Internal Helpers -----------------------------------------------

    def _touch(self) -> None:
        """Update timestamp and increment optimistic concurrency version."""
        self.updated_at = datetime.now(timezone.utc)
        self.version += 1

    def _record_event(self, event: InvoiceDomainEvent) -> None:
        self._events.append(event)

    def get_line(self, line_id: InvoiceLineId) -> InvoiceLine | None:
        return self._lines.get(line_id.value)

    # -- Line Item Management -------------------------------------------

    def add_line(
        self,
        medicine_id: MedicineId,
        quantity: InvoiceQuantity,
        unit_price: UnitPrice,
        batch_id: MedicineBatchId | None = None,
        discount: DiscountAmount = DiscountAmount.none(),
        tax_rate: TaxRate = TaxRate.zero(),
        line_id: InvoiceLineId | None = None,
    ) -> InvoiceLine:
        """Add a new line item to a draft invoice."""
        if self.status != InvoiceStatus.DRAFT:
            raise InvalidInvoiceStateError(
                self.id.value, self.status.value, "MODIFICATION"
            )
        if quantity.value <= 0:
            raise InvalidInvoiceQuantityError(quantity.value, "invoice quantity must be positive")

        for existing_line in self._lines.values():
            if existing_line.medicine_id == medicine_id and existing_line.batch_id == batch_id and not existing_line.is_cancelled:
                raise DuplicateInvoiceLineError(self.id.value, medicine_id.value)

        il_id = line_id if line_id is not None else InvoiceLineId.generate()
        now = datetime.now(timezone.utc)
        line = InvoiceLine(
            id=il_id,
            medicine_id=medicine_id,
            batch_id=batch_id,
            quantity=quantity,
            unit_price=unit_price,
            discount=discount,
            tax_rate=tax_rate,
            tax_type=self.tax_type,
            created_at=now,
            updated_at=now,
        )
        self._lines[il_id.value] = line
        self._touch()

        self._record_event(
            InvoiceLineAdded(
                invoice_id=self.id,
                line_id=il_id,
                medicine_id=medicine_id,
                batch_id=batch_id,
                quantity=quantity,
                unit_price=unit_price.value,
            )
        )
        return line

    def remove_line(self, line_id: InvoiceLineId) -> None:
        """Remove a line item from a draft invoice."""
        if self.status != InvoiceStatus.DRAFT:
            raise InvalidInvoiceStateError(
                self.id.value, self.status.value, "MODIFICATION"
            )
        if line_id.value not in self._lines:
            raise InvoiceLineNotFoundError(self.id.value, line_id.value)

        line = self._lines.pop(line_id.value)
        self._touch()

        self._record_event(
            InvoiceLineRemoved(
                invoice_id=self.id,
                line_id=line.id,
                medicine_id=line.medicine_id,
            )
        )

    # -- Lifecycle Transitions ------------------------------------------

    def issue(self) -> None:
        """Finalize and issue a draft invoice."""
        if self.status != InvoiceStatus.DRAFT:
            raise InvalidInvoiceStateError(
                self.id.value, self.status.value, InvoiceStatus.ISSUED.value
            )
        active_lines = [l for l in self._lines.values() if not l.is_cancelled]
        if not active_lines:
            raise InvalidInvoiceLineError("cannot issue an invoice with no active line items")

        total = self.calculate_total()
        self.status = InvoiceStatus.ISSUED
        self._touch()

        self._record_event(
            InvoiceIssued(
                invoice_id=self.id,
                number=self.number,
                total_amount=total.net_total,
            )
        )

    def record_payment(self, amount_paid: Money) -> None:
        """Record customer payment against an issued or partially paid invoice."""
        if self.status in (InvoiceStatus.CANCELLED, InvoiceStatus.VOID):
            raise InvalidPaymentStateError(
                self.id.value, self.payment_status.value, "PAYMENT_ON_CANCELLED"
            )
        if self.status not in (InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID, InvoiceStatus.DRAFT):
            raise InvalidInvoiceStateError(
                self.id.value, self.status.value, "PAYMENT"
            )
        if amount_paid.is_zero():
            return

        total = self.calculate_total()
        new_total_paid = self.total_amount_paid.add(amount_paid)

        if new_total_paid > total.net_total:
            outstanding = total.net_total.subtract(self.total_amount_paid) if total.net_total >= self.total_amount_paid else Money.zero(total.net_total.currency)
            raise OverpaymentError(
                self.id.value,
                paying_amount=amount_paid.amount,
                outstanding_amount=outstanding.amount,
            )

        self.total_amount_paid = new_total_paid
        remaining = total.net_total.subtract(self.total_amount_paid)

        if remaining.is_zero():
            self.payment_status = PaymentStatus.PAID
            self.status = InvoiceStatus.PAID
            self._touch()
            self._record_event(
                InvoicePaid(
                    invoice_id=self.id,
                    number=self.number,
                    total_amount=total.net_total,
                )
            )
        else:
            self.payment_status = PaymentStatus.PARTIALLY_PAID
            self.status = InvoiceStatus.PARTIALLY_PAID
            self._touch()
            self._record_event(
                InvoicePartiallyPaid(
                    invoice_id=self.id,
                    amount_paid=amount_paid,
                    remaining_balance=remaining,
                )
            )

        self._record_event(
            InvoicePaymentRecorded(
                invoice_id=self.id,
                amount_paid=amount_paid,
                payment_status=self.payment_status.value,
                remaining_balance=remaining,
            )
        )

    def cancel(self, reason: str) -> None:
        """Cancel an invoice."""
        clean_reason = reason.strip()
        if not clean_reason:
            raise InvalidInvoiceLineError("cancellation reason is required")

        if self.status == InvoiceStatus.CANCELLED:
            raise InvoiceAlreadyCancelledError(self.id.value)

        if self.status == InvoiceStatus.PAID:
            raise InvoiceNotCancellableError(
                self.id.value, self.status.value, "fully paid invoices cannot be cancelled directly"
            )

        self.status = InvoiceStatus.CANCELLED
        for line in self._lines.values():
            line.status = InvoiceLineStatus.CANCELLED

        self._touch()

        self._record_event(
            InvoiceCancelled(
                invoice_id=self.id,
                reason=clean_reason,
            )
        )

    # -- Overall Monetary Total -----------------------------------------

    def calculate_total(self) -> InvoiceTotal:
        """Calculates total financial summary across all active line items including CGST, SGST, IGST breakdown."""
        active_lines = [l for l in self._lines.values() if not l.is_cancelled]
        if not active_lines:
            return InvoiceTotal.zero()

        first_currency = active_lines[0].calculate_subtotal().currency
        subtotal = Money.zero(first_currency)
        total_discount = Money.zero(first_currency)
        cgst_amount = Money.zero(first_currency)
        sgst_amount = Money.zero(first_currency)
        igst_amount = Money.zero(first_currency)

        for line in active_lines:
            subtotal = subtotal.add(line.calculate_subtotal())
            total_discount = total_discount.add(line.calculate_discount_amount())
            gst_bd = line.calculate_gst_breakdown()
            cgst_amount = cgst_amount.add(gst_bd.cgst)
            sgst_amount = sgst_amount.add(gst_bd.sgst)
            igst_amount = igst_amount.add(gst_bd.igst)

        return InvoiceTotal.create(
            subtotal=subtotal,
            total_discount=total_discount,
            cgst_amount=cgst_amount,
            sgst_amount=sgst_amount,
            igst_amount=igst_amount,
        )
