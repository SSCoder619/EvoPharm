"""Entities for the Purchase bounded context.

Following DDD principles, Purchase is the Aggregate Root representing procurement
of medicines from suppliers. PurchaseLine is a child entity belonging exclusively
to a Purchase aggregate.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

from ..medicine.value_objects import MedicineId
from .domain_events import (
    PurchaseApproved,
    PurchaseCancelled,
    PurchaseCreated,
    PurchaseDomainEvent,
    PurchaseInvoiceAttached,
    PurchaseLineAdded,
    PurchaseLineRemoved,
    PurchaseOrdered,
    PurchasePartiallyReceived,
    PurchasePaymentRecorded,
    PurchaseReceived,
)
from .enums import (
    PaymentStatus,
    PurchaseLineStatus,
    PurchaseStatus,
    ReceivingStatus,
)
from .exceptions import (
    DuplicatePurchaseLineError,
    ExceededOrderedQuantityError,
    InvalidInvoiceReferenceError,
    InvalidPaymentStateTransitionError,
    InvalidPurchaseLineError,
    InvalidPurchaseQuantityError,
    InvalidPurchaseStateTransitionError,
    PurchaseAlreadyCancelledError,
    PurchaseLineNotFoundError,
    PurchaseNotCancellableError,
    ReceivingAgainstCancelledPurchaseError,
)
from .value_objects import (
    Discount,
    InvoiceReference,
    Money,
    PurchaseId,
    PurchaseLineId,
    PurchaseOrderReference,
    PurchaseQuantity,
    PurchaseTotal,
    SupplierReference,
    TaxRate,
    UnitPrice,
)


@dataclass(slots=True, eq=False)
class PurchaseLine:
    """Child entity representing an individual item line in a purchase order."""

    id: PurchaseLineId
    medicine_id: MedicineId
    ordered_quantity: PurchaseQuantity
    unit_price: UnitPrice
    received_quantity: PurchaseQuantity = field(default_factory=PurchaseQuantity.zero)
    discount: Discount = field(default_factory=Discount.none)
    tax_rate: TaxRate = field(default_factory=TaxRate.zero)
    status: PurchaseLineStatus = PurchaseLineStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PurchaseLine):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def outstanding_quantity(self) -> PurchaseQuantity:
        """Quantity remaining to be received for this line."""
        if self.status == PurchaseLineStatus.CANCELLED:
            return PurchaseQuantity.zero()
        return self.ordered_quantity.subtract(self.received_quantity)

    @property
    def is_fully_received(self) -> bool:
        """Indicates if the full ordered quantity has been received."""
        return self.received_quantity.value >= self.ordered_quantity.value

    @property
    def is_cancelled(self) -> bool:
        return self.status == PurchaseLineStatus.CANCELLED

    # -- Monetary calculations ------------------------------------------

    def calculate_subtotal(self) -> Money:
        """Raw subtotal before discount and tax."""
        return self.unit_price.multiply(self.ordered_quantity)

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

    def receive(self, quantity: PurchaseQuantity) -> None:
        """Record received stock quantity for this line."""
        if self.is_cancelled:
            raise InvalidPurchaseLineError("cannot receive against a cancelled purchase line")
        if quantity.value <= 0:
            raise InvalidPurchaseQuantityError(quantity.value, "received quantity must be strictly positive")
        
        new_received = self.received_quantity.value + quantity.value
        if new_received > self.ordered_quantity.value:
            raise ExceededOrderedQuantityError(
                line_id=self.id.value,
                ordered=self.ordered_quantity.value,
                receiving=quantity.value,
                previously_received=self.received_quantity.value,
            )

        self.received_quantity = PurchaseQuantity(new_received)
        if self.received_quantity.value == self.ordered_quantity.value:
            self.status = PurchaseLineStatus.RECEIVED
        else:
            self.status = PurchaseLineStatus.PARTIALLY_RECEIVED
        self._touch()

    def cancel(self) -> None:
        """Cancel this line item."""
        if self.status == PurchaseLineStatus.RECEIVED:
            raise InvalidPurchaseLineError("cannot cancel an already fully received line")
        self.status = PurchaseLineStatus.CANCELLED
        self._touch()


@dataclass(slots=True, eq=False)
class Purchase:
    """Aggregate Root representing a procurement transaction / Purchase Order."""

    id: PurchaseId
    supplier_reference: SupplierReference
    order_reference: PurchaseOrderReference
    invoice_reference: InvoiceReference | None = None
    purchase_status: PurchaseStatus = PurchaseStatus.DRAFT
    receiving_status: ReceivingStatus = ReceivingStatus.PENDING
    payment_status: PaymentStatus = PaymentStatus.UNPAID
    total_amount_paid: Money = field(default_factory=Money.zero)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1
    _lines: dict[UUID, PurchaseLine] = field(default_factory=dict)
    _events: list[PurchaseDomainEvent] = field(default_factory=list)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Purchase):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    # -- Factory --------------------------------------------------------

    @classmethod
    def create(
        cls,
        supplier_reference: SupplierReference,
        order_reference: PurchaseOrderReference,
        invoice_reference: InvoiceReference | None = None,
        id: PurchaseId | None = None,
    ) -> "Purchase":
        """Initialize a new Purchase Order aggregate root."""
        p_id = id if id is not None else PurchaseId.generate()
        now = datetime.now(timezone.utc)
        purchase = cls(
            id=p_id,
            supplier_reference=supplier_reference,
            order_reference=order_reference,
            invoice_reference=invoice_reference,
            purchase_status=PurchaseStatus.DRAFT,
            receiving_status=ReceivingStatus.PENDING,
            payment_status=PaymentStatus.UNPAID,
            created_at=now,
            updated_at=now,
        )
        purchase._record_event(
            PurchaseCreated(
                purchase_id=p_id,
                supplier_reference=supplier_reference,
                order_reference=order_reference,
            )
        )
        return purchase

    # -- Properties & Views ---------------------------------------------

    @property
    def lines(self) -> tuple[PurchaseLine, ...]:
        """Read-only tuple of line items in this purchase order."""
        return tuple(self._lines.values())

    @property
    def events(self) -> tuple[PurchaseDomainEvent, ...]:
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

    def _record_event(self, event: PurchaseDomainEvent) -> None:
        self._events.append(event)

    def get_line(self, line_id: PurchaseLineId) -> PurchaseLine | None:
        return self._lines.get(line_id.value)

    # -- Line Item Management -------------------------------------------

    def add_line(
        self,
        medicine_id: MedicineId,
        ordered_quantity: PurchaseQuantity,
        unit_price: UnitPrice,
        discount: Discount = Discount.none(),
        tax_rate: TaxRate = TaxRate.zero(),
        line_id: PurchaseLineId | None = None,
    ) -> PurchaseLine:
        """Add a new line item to a draft purchase order."""
        if self.purchase_status != PurchaseStatus.DRAFT:
            raise InvalidPurchaseStateTransitionError(
                self.id.value, self.purchase_status.value, "MODIFICATION"
            )
        if ordered_quantity.value <= 0:
            raise InvalidPurchaseQuantityError(ordered_quantity.value, "ordered quantity must be positive")

        for existing_line in self._lines.values():
            if existing_line.medicine_id == medicine_id and not existing_line.is_cancelled:
                raise DuplicatePurchaseLineError(self.id.value, medicine_id.value)

        pl_id = line_id if line_id is not None else PurchaseLineId.generate()
        now = datetime.now(timezone.utc)
        line = PurchaseLine(
            id=pl_id,
            medicine_id=medicine_id,
            ordered_quantity=ordered_quantity,
            unit_price=unit_price,
            discount=discount,
            tax_rate=tax_rate,
            created_at=now,
            updated_at=now,
        )
        self._lines[pl_id.value] = line
        self._touch()

        self._record_event(
            PurchaseLineAdded(
                purchase_id=self.id,
                line_id=pl_id,
                medicine_id=medicine_id,
                ordered_quantity=ordered_quantity,
                unit_price=unit_price.value,
            )
        )
        return line

    def remove_line(self, line_id: PurchaseLineId) -> None:
        """Remove a line item from a draft purchase order."""
        if self.purchase_status != PurchaseStatus.DRAFT:
            raise InvalidPurchaseStateTransitionError(
                self.id.value, self.purchase_status.value, "MODIFICATION"
            )
        if line_id.value not in self._lines:
            raise PurchaseLineNotFoundError(self.id.value, line_id.value)

        line = self._lines.pop(line_id.value)
        self._touch()

        self._record_event(
            PurchaseLineRemoved(
                purchase_id=self.id,
                line_id=line.id,
                medicine_id=line.medicine_id,
            )
        )

    # -- Lifecycle State Transitions ------------------------------------

    def approve(self, approved_by_user_id: UUID | None = None) -> None:
        """Approve a draft purchase order."""
        if self.purchase_status != PurchaseStatus.DRAFT:
            raise InvalidPurchaseStateTransitionError(
                self.id.value, self.purchase_status.value, PurchaseStatus.APPROVED.value
            )
        active_lines = [l for l in self._lines.values() if not l.is_cancelled]
        if not active_lines:
            raise InvalidPurchaseLineError("cannot approve a purchase order with no active line items")

        self.purchase_status = PurchaseStatus.APPROVED
        self._touch()

        self._record_event(
            PurchaseApproved(
                purchase_id=self.id,
                approved_by_user_id=approved_by_user_id,
            )
        )

    def place_order(self) -> None:
        """Transmit / place an approved purchase order with supplier."""
        if self.purchase_status != PurchaseStatus.APPROVED:
            raise InvalidPurchaseStateTransitionError(
                self.id.value, self.purchase_status.value, PurchaseStatus.ORDERED.value
            )
        self.purchase_status = PurchaseStatus.ORDERED
        self._touch()

        self._record_event(
            PurchaseOrdered(
                purchase_id=self.id,
                supplier_reference=self.supplier_reference,
            )
        )

    # -- Receiving Stock ------------------------------------------------

    def receive_stock(
        self,
        line_id: PurchaseLineId,
        quantity: PurchaseQuantity,
        batch_number: str,
    ) -> None:
        """Receive stock units against an ordered purchase line."""
        if self.purchase_status in (PurchaseStatus.CANCELLED, PurchaseStatus.REJECTED):
            raise ReceivingAgainstCancelledPurchaseError(self.id.value)

        if self.purchase_status not in (PurchaseStatus.ORDERED, PurchaseStatus.PARTIALLY_RECEIVED):
            raise InvalidPurchaseStateTransitionError(
                self.id.value, self.purchase_status.value, "RECEIVING"
            )

        line = self.get_line(line_id)
        if line is None:
            raise PurchaseLineNotFoundError(self.id.value, line_id.value)

        line.receive(quantity)

        # Update receiving and purchase status aggregates
        active_lines = [l for l in self._lines.values() if not l.is_cancelled]
        all_fully_received = all(l.is_fully_received for l in active_lines)
        any_received = any(l.received_quantity.value > 0 for l in active_lines)

        if all_fully_received:
            self.receiving_status = ReceivingStatus.COMPLETED
            self.purchase_status = PurchaseStatus.RECEIVED
            self._record_event(
                PurchaseReceived(
                    purchase_id=self.id,
                    total_items_received=len(active_lines),
                )
            )
        elif any_received:
            self.receiving_status = ReceivingStatus.PARTIAL
            self.purchase_status = PurchaseStatus.PARTIALLY_RECEIVED

        self._touch()

        self._record_event(
            PurchasePartiallyReceived(
                purchase_id=self.id,
                line_id=line.id,
                medicine_id=line.medicine_id,
                received_quantity=quantity,
                batch_number=batch_number,
                remaining_quantity=line.outstanding_quantity,
            )
        )

    # -- Cancellation & Invoicing & Payments ----------------------------

    def cancel(self, reason: str) -> None:
        """Cancel a purchase order."""
        clean_reason = reason.strip()
        if not clean_reason:
            raise InvalidPurchaseLineError("cancellation reason is required")

        if self.purchase_status == PurchaseStatus.CANCELLED:
            raise PurchaseAlreadyCancelledError(self.id.value)

        if self.purchase_status == PurchaseStatus.RECEIVED or self.receiving_status == ReceivingStatus.COMPLETED:
            raise PurchaseNotCancellableError(
                self.id.value, self.purchase_status.value, "fully received purchases cannot be cancelled"
            )

        self.purchase_status = PurchaseStatus.CANCELLED
        self.receiving_status = ReceivingStatus.CANCELLED
        for line in self._lines.values():
            if not line.is_fully_received:
                line.status = PurchaseLineStatus.CANCELLED

        self._touch()

        self._record_event(
            PurchaseCancelled(
                purchase_id=self.id,
                reason=clean_reason,
            )
        )

    def attach_invoice(self, invoice_reference: InvoiceReference) -> None:
        """Attach commercial invoice reference."""
        if self.purchase_status == PurchaseStatus.CANCELLED:
            raise InvalidInvoiceReferenceError(
                invoice_reference.value, "cannot attach invoice to a cancelled purchase"
            )
        self.invoice_reference = invoice_reference
        self._touch()

        self._record_event(
            PurchaseInvoiceAttached(
                purchase_id=self.id,
                invoice_reference=invoice_reference,
            )
        )

    def record_payment(self, amount_paid: Money) -> None:
        """Record commercial payment settlement."""
        if self.purchase_status == PurchaseStatus.CANCELLED:
            raise InvalidPaymentStateTransitionError(
                self.id.value, self.payment_status.value, "PAYMENT_ON_CANCELLED"
            )
        if amount_paid.is_zero():
            return

        self.total_amount_paid = self.total_amount_paid.add(amount_paid)
        total = self.calculate_total()
        if self.total_amount_paid >= total.net_total:
            self.payment_status = PaymentStatus.PAID
        else:
            self.payment_status = PaymentStatus.PARTIALLY_PAID

        self._touch()

        self._record_event(
            PurchasePaymentRecorded(
                purchase_id=self.id,
                amount_paid=amount_paid,
                payment_status=self.payment_status.value,
            )
        )

    # -- Overall Monetary Total -----------------------------------------

    def calculate_total(self) -> PurchaseTotal:
        """Calculates total financial summary across all active line items."""
        active_lines = [l for l in self._lines.values() if not l.is_cancelled]
        if not active_lines:
            return PurchaseTotal.zero()

        first_currency = active_lines[0].calculate_subtotal().currency
        subtotal = Money.zero(first_currency)
        total_discount = Money.zero(first_currency)
        total_tax = Money.zero(first_currency)

        for line in active_lines:
            subtotal = subtotal.add(line.calculate_subtotal())
            total_discount = total_discount.add(line.calculate_discount_amount())
            total_tax = total_tax.add(line.calculate_tax_amount())

        return PurchaseTotal.create(
            subtotal=subtotal,
            total_discount=total_discount,
            total_tax=total_tax,
        )
