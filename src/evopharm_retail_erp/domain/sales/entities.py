"""Entities for the Sales bounded context.

Following DDD principles, Sale is the Aggregate Root representing a retail
dispensing transaction with a customer. SaleLine is a child entity belonging exclusively
to a Sale aggregate.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from ..medicine.value_objects import MedicineBatchId, MedicineId
from .domain_events import (
    PrescriptionAttached,
    SaleCancelled,
    SaleCompleted,
    SaleConfirmed,
    SaleCreated,
    SaleLineAdded,
    SaleLineRemoved,
    SalePaymentRecorded,
    SaleReturned,
    SalesDomainEvent,
)
from .enums import (
    PaymentMethod,
    PaymentStatus,
    ReturnReason,
    SaleLineStatus,
    SaleStatus,
)
from .exceptions import (
    DuplicateSaleLineError,
    ExceededSoldQuantityError,
    InvalidInvoiceNumberError,
    InvalidPaymentStateError,
    InvalidPrescriptionReferenceError,
    InvalidSaleLineError,
    InvalidSaleQuantityError,
    InvalidSaleStateError,
    ReceivingReturnAgainstCancelledSaleError,
    SaleAlreadyCancelledError,
    SaleLineNotFoundError,
    SaleNotCancellableError,
)
from .value_objects import (
    CustomerReference,
    Discount,
    InvoiceNumber,
    Money,
    PaymentReference,
    PrescriptionReference,
    SaleId,
    SaleLineId,
    SaleQuantity,
    SaleTotal,
    TaxRate,
    UnitPrice,
)


@dataclass(slots=True, eq=False)
class SaleLine:
    """Child entity representing an individual item line in a retail sale."""

    id: SaleLineId
    medicine_id: MedicineId
    quantity: SaleQuantity
    unit_price: UnitPrice
    batch_id: MedicineBatchId | None = None
    returned_quantity: SaleQuantity = field(default_factory=SaleQuantity.zero)
    discount: Discount = field(default_factory=Discount.none)
    tax_rate: TaxRate = field(default_factory=TaxRate.zero)
    status: SaleLineStatus = SaleLineStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SaleLine):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def net_quantity(self) -> SaleQuantity:
        """Quantity remaining after deducting customer returns."""
        if self.status == SaleLineStatus.CANCELLED:
            return SaleQuantity.zero()
        return self.quantity.subtract(self.returned_quantity)

    @property
    def is_fully_returned(self) -> bool:
        return self.returned_quantity.value >= self.quantity.value

    @property
    def is_cancelled(self) -> bool:
        return self.status == SaleLineStatus.CANCELLED

    # -- Monetary calculations ------------------------------------------

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

    def calculate_tax_amount(self) -> Money:
        """GST / Tax amount calculated on taxable base."""
        taxable = self.calculate_taxable_amount()
        return self.tax_rate.calculate_tax_amount(taxable)

    def calculate_line_total(self) -> Money:
        """Final net total for this line (taxable + tax)."""
        taxable = self.calculate_taxable_amount()
        tax = self.calculate_tax_amount()
        return taxable.add(tax)

    # -- State mutations ------------------------------------------------

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    def process_return(self, quantity: SaleQuantity) -> Money:
        """Process customer return for this line item and return refund amount."""
        if self.is_cancelled:
            raise InvalidSaleLineError("cannot process return against a cancelled sale line")
        if quantity.value <= 0:
            raise InvalidSaleQuantityError(quantity.value, "return quantity must be strictly positive")

        new_returned = self.returned_quantity.value + quantity.value
        if new_returned > self.quantity.value:
            raise ExceededSoldQuantityError(
                line_id=self.id.value,
                sold=self.quantity.value,
                returning=quantity.value,
                previously_returned=self.returned_quantity.value,
            )

        self.returned_quantity = SaleQuantity(new_returned)
        if self.returned_quantity.value == self.quantity.value:
            self.status = SaleLineStatus.RETURNED

        self._touch()
        # Pro-rata refund amount based on line total per unit
        unit_net = self.calculate_line_total().multiply(quantity.value)
        refund = Money(
            amount=unit_net.amount / Decimal(str(self.quantity.value)),
            currency=unit_net.currency,
        )
        return refund

    def cancel(self) -> None:
        """Cancel this line item."""
        if self.status == SaleLineStatus.RETURNED:
            raise InvalidSaleLineError("cannot cancel an already returned sale line")
        self.status = SaleLineStatus.CANCELLED
        self._touch()


@dataclass(slots=True, eq=False)
class Sale:
    """Aggregate Root representing a retail sales dispensing transaction."""

    id: SaleId
    customer_reference: CustomerReference
    invoice_number: InvoiceNumber
    prescription_reference: PrescriptionReference | None = None
    sale_status: SaleStatus = SaleStatus.DRAFT
    payment_status: PaymentStatus = PaymentStatus.UNPAID
    payment_method: PaymentMethod | None = None
    total_amount_paid: Money = field(default_factory=Money.zero)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1
    _lines: dict[UUID, SaleLine] = field(default_factory=dict)
    _events: list[SalesDomainEvent] = field(default_factory=list)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Sale):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    # -- Factory --------------------------------------------------------

    @classmethod
    def create(
        cls,
        customer_reference: CustomerReference | None = None,
        invoice_number: InvoiceNumber | None = None,
        prescription_reference: PrescriptionReference | None = None,
        id: SaleId | None = None,
    ) -> "Sale":
        """Initialize a new retail Sale aggregate root."""
        s_id = id if id is not None else SaleId.generate()
        cust_ref = customer_reference if customer_reference is not None else CustomerReference.walk_in()
        inv_num = invoice_number if invoice_number is not None else InvoiceNumber(f"INV-{s_id.value.hex[:8].upper()}")
        now = datetime.now(timezone.utc)

        sale = cls(
            id=s_id,
            customer_reference=cust_ref,
            invoice_number=inv_num,
            prescription_reference=prescription_reference,
            sale_status=SaleStatus.DRAFT,
            payment_status=PaymentStatus.UNPAID,
            created_at=now,
            updated_at=now,
        )
        sale._record_event(
            SaleCreated(
                sale_id=s_id,
                customer_reference=cust_ref,
                invoice_number=inv_num,
            )
        )
        return sale

    # -- Properties & Views ---------------------------------------------

    @property
    def lines(self) -> tuple[SaleLine, ...]:
        """Read-only tuple of line items in this retail sale."""
        return tuple(self._lines.values())

    @property
    def events(self) -> tuple[SalesDomainEvent, ...]:
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

    def _record_event(self, event: SalesDomainEvent) -> None:
        self._events.append(event)

    def get_line(self, line_id: SaleLineId) -> SaleLine | None:
        return self._lines.get(line_id.value)

    # -- Line Item Management -------------------------------------------

    def add_line(
        self,
        medicine_id: MedicineId,
        quantity: SaleQuantity,
        unit_price: UnitPrice,
        batch_id: MedicineBatchId | None = None,
        discount: Discount = Discount.none(),
        tax_rate: TaxRate = TaxRate.zero(),
        line_id: SaleLineId | None = None,
    ) -> SaleLine:
        """Add a new line item to a draft retail sale."""
        if self.sale_status != SaleStatus.DRAFT:
            raise InvalidSaleStateError(
                self.id.value, self.sale_status.value, "MODIFICATION"
            )
        if quantity.value <= 0:
            raise InvalidSaleQuantityError(quantity.value, "sale quantity must be positive")

        for existing_line in self._lines.values():
            if existing_line.medicine_id == medicine_id and existing_line.batch_id == batch_id and not existing_line.is_cancelled:
                raise DuplicateSaleLineError(self.id.value, medicine_id.value)

        sl_id = line_id if line_id is not None else SaleLineId.generate()
        now = datetime.now(timezone.utc)
        line = SaleLine(
            id=sl_id,
            medicine_id=medicine_id,
            batch_id=batch_id,
            quantity=quantity,
            unit_price=unit_price,
            discount=discount,
            tax_rate=tax_rate,
            created_at=now,
            updated_at=now,
        )
        self._lines[sl_id.value] = line
        self._touch()

        self._record_event(
            SaleLineAdded(
                sale_id=self.id,
                line_id=sl_id,
                medicine_id=medicine_id,
                batch_id=batch_id,
                quantity=quantity,
                unit_price=unit_price.value,
            )
        )
        return line

    def remove_line(self, line_id: SaleLineId) -> None:
        """Remove a line item from a draft retail sale."""
        if self.sale_status != SaleStatus.DRAFT:
            raise InvalidSaleStateError(
                self.id.value, self.sale_status.value, "MODIFICATION"
            )
        if line_id.value not in self._lines:
            raise SaleLineNotFoundError(self.id.value, line_id.value)

        line = self._lines.pop(line_id.value)
        self._touch()

        self._record_event(
            SaleLineRemoved(
                sale_id=self.id,
                line_id=line.id,
                medicine_id=line.medicine_id,
            )
        )

    def attach_prescription(self, prescription_reference: PrescriptionReference) -> None:
        """Attach medical practitioner prescription details to sale."""
        self.prescription_reference = prescription_reference
        self._touch()

        self._record_event(
            PrescriptionAttached(
                sale_id=self.id,
                prescription_reference=prescription_reference,
            )
        )

    # -- Lifecycle Transitions ------------------------------------------

    def confirm(self) -> None:
        """Confirm a draft retail sale for billing and stock allocation."""
        if self.sale_status != SaleStatus.DRAFT:
            raise InvalidSaleStateError(
                self.id.value, self.sale_status.value, SaleStatus.CONFIRMED.value
            )
        active_lines = [l for l in self._lines.values() if not l.is_cancelled]
        if not active_lines:
            raise InvalidSaleLineError("cannot confirm a retail sale with no active line items")

        total = self.calculate_total()
        self.sale_status = SaleStatus.CONFIRMED
        self._touch()

        self._record_event(
            SaleConfirmed(
                sale_id=self.id,
                total_amount=total.net_total,
            )
        )

    def record_payment(
        self,
        amount_paid: Money,
        payment_method: PaymentMethod = PaymentMethod.CASH,
        payment_reference: PaymentReference | None = None,
    ) -> None:
        """Record customer payment settlement for a sale."""
        if self.sale_status == SaleStatus.CANCELLED:
            raise InvalidPaymentStateError(
                self.id.value, self.payment_status.value, "PAYMENT_ON_CANCELLED"
            )
        if self.sale_status not in (SaleStatus.CONFIRMED, SaleStatus.PAID):
            raise InvalidSaleStateError(
                self.id.value, self.sale_status.value, "PAYMENT"
            )
        if amount_paid.is_zero():
            return

        self.total_amount_paid = self.total_amount_paid.add(amount_paid)
        self.payment_method = payment_method
        total = self.calculate_total()

        if self.total_amount_paid >= total.net_total:
            self.payment_status = PaymentStatus.PAID
            self.sale_status = SaleStatus.PAID
        else:
            self.payment_status = PaymentStatus.PARTIALLY_PAID

        self._touch()

        self._record_event(
            SalePaymentRecorded(
                sale_id=self.id,
                amount_paid=amount_paid,
                payment_method=payment_method.value,
                payment_status=self.payment_status.value,
                payment_reference=payment_reference,
            )
        )

    def complete(self) -> None:
        """Mark a paid sale as fully completed."""
        if self.sale_status not in (SaleStatus.PAID, SaleStatus.CONFIRMED):
            raise InvalidSaleStateError(
                self.id.value, self.sale_status.value, SaleStatus.COMPLETED.value
            )
        self.sale_status = SaleStatus.COMPLETED
        self._touch()

        self._record_event(
            SaleCompleted(
                sale_id=self.id,
                invoice_number=self.invoice_number,
            )
        )

    def cancel(self, reason: str) -> None:
        """Cancel a retail sale."""
        clean_reason = reason.strip()
        if not clean_reason:
            raise InvalidSaleLineError("cancellation reason is required")

        if self.sale_status == SaleStatus.CANCELLED:
            raise SaleAlreadyCancelledError(self.id.value)

        if self.sale_status == SaleStatus.COMPLETED:
            raise SaleNotCancellableError(
                self.id.value, self.sale_status.value, "completed sales cannot be cancelled; process a return instead"
            )

        self.sale_status = SaleStatus.CANCELLED
        for line in self._lines.values():
            line.status = SaleLineStatus.CANCELLED

        self._touch()

        self._record_event(
            SaleCancelled(
                sale_id=self.id,
                reason=clean_reason,
            )
        )

    # -- Returns & Refunds ----------------------------------------------

    def process_return(
        self,
        line_id: SaleLineId,
        quantity: SaleQuantity,
        reason: ReturnReason = ReturnReason.CUSTOMER_CHANGED_MIND,
    ) -> Money:
        """Process customer return against a sale line."""
        if self.sale_status == SaleStatus.CANCELLED:
            raise ReceivingReturnAgainstCancelledSaleError(self.id.value)

        if self.sale_status not in (SaleStatus.COMPLETED, SaleStatus.PAID, SaleStatus.RETURNED):
            raise InvalidSaleStateError(
                self.id.value, self.sale_status.value, "RETURN"
            )

        line = self.get_line(line_id)
        if line is None:
            raise SaleLineNotFoundError(self.id.value, line_id.value)

        refund_amount = line.process_return(quantity)

        active_lines = [l for l in self._lines.values() if not l.is_cancelled]
        all_returned = all(l.is_fully_returned for l in active_lines)

        if all_returned:
            self.sale_status = SaleStatus.RETURNED
            self.payment_status = PaymentStatus.REFUNDED

        self._touch()

        self._record_event(
            SaleReturned(
                sale_id=self.id,
                line_id=line.id,
                medicine_id=line.medicine_id,
                batch_id=line.batch_id,
                returned_quantity=quantity,
                return_reason=reason.value,
                refund_amount=refund_amount,
            )
        )

        return refund_amount

    # -- Overall Monetary Total -----------------------------------------

    def calculate_total(self) -> SaleTotal:
        """Calculates total financial summary across all active line items."""
        active_lines = [l for l in self._lines.values() if not l.is_cancelled]
        if not active_lines:
            return SaleTotal.zero()

        first_currency = active_lines[0].calculate_subtotal().currency
        subtotal = Money.zero(first_currency)
        total_discount = Money.zero(first_currency)
        total_tax = Money.zero(first_currency)

        for line in active_lines:
            subtotal = subtotal.add(line.calculate_subtotal())
            total_discount = total_discount.add(line.calculate_discount_amount())
            total_tax = total_tax.add(line.calculate_tax_amount())

        return SaleTotal.create(
            subtotal=subtotal,
            total_discount=total_discount,
            total_tax=total_tax,
        )
