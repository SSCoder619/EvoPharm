"""Domain exceptions for the Invoice bounded context.

Every exception here is raised from inside an invoice aggregate, entity, or value
object to protect a business invariant. None of them carry any dependency on
infrastructure or presentation concerns — translating a domain error into a UI
message or an API response is a job for an outer layer, not for the domain.
"""
from __future__ import annotations

from uuid import UUID


class InvoiceDomainError(Exception):
    """Base class for every error raised by the Invoice domain."""


class InvalidInvoiceStateError(InvoiceDomainError):
    def __init__(self, invoice_id: UUID, current_status: str, target_status: str) -> None:
        self.invoice_id = invoice_id
        self.current_status = current_status
        self.target_status = target_status
        super().__init__(
            f"Cannot transition invoice {invoice_id} from status "
            f"{current_status!r} to {target_status!r}"
        )


class InvalidInvoiceNumberError(InvoiceDomainError):
    def __init__(self, value: str, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid invoice number {value!r}: {reason}")


class InvalidInvoiceLineError(InvoiceDomainError):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid invoice line: {reason}")


class InvalidInvoiceQuantityError(InvoiceDomainError):
    def __init__(self, value: object, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid invoice quantity {value!r}: {reason}")


class InvalidInvoiceAmountError(InvoiceDomainError):
    def __init__(self, value: object, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid invoice amount {value!r}: {reason}")


class InvalidTaxRateError(InvoiceDomainError):
    def __init__(self, value: object, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid tax rate {value!r}: {reason}")


class DuplicateInvoiceLineError(InvoiceDomainError):
    def __init__(self, invoice_id: UUID, item_id: UUID) -> None:
        self.invoice_id = invoice_id
        self.item_id = item_id
        super().__init__(
            f"Invoice {invoice_id} already contains a line for item {item_id}"
        )


class InvoiceLineNotFoundError(InvoiceDomainError):
    def __init__(self, invoice_id: UUID, line_id: UUID) -> None:
        self.invoice_id = invoice_id
        self.line_id = line_id
        super().__init__(
            f"Invoice line {line_id} not found in invoice {invoice_id}"
        )


class InvoiceAlreadyCancelledError(InvoiceDomainError):
    def __init__(self, invoice_id: UUID) -> None:
        self.invoice_id = invoice_id
        super().__init__(f"Invoice {invoice_id} is already cancelled")


class InvoiceNotCancellableError(InvoiceDomainError):
    def __init__(self, invoice_id: UUID, current_status: str, reason: str) -> None:
        self.invoice_id = invoice_id
        self.current_status = current_status
        self.reason = reason
        super().__init__(
            f"Invoice {invoice_id} in status {current_status!r} cannot be cancelled: {reason}"
        )


class InvalidPaymentStateError(InvoiceDomainError):
    def __init__(self, invoice_id: UUID, current_status: str, target_status: str) -> None:
        self.invoice_id = invoice_id
        self.current_status = current_status
        self.target_status = target_status
        super().__init__(
            f"Cannot transition payment for invoice {invoice_id} from "
            f"{current_status!r} to {target_status!r}"
        )


class OverpaymentError(InvoiceDomainError):
    def __init__(self, invoice_id: UUID, paying_amount: object, outstanding_amount: object) -> None:
        self.invoice_id = invoice_id
        self.paying_amount = paying_amount
        self.outstanding_amount = outstanding_amount
        super().__init__(
            f"Payment amount {paying_amount!r} exceeds outstanding balance {outstanding_amount!r} "
            f"for invoice {invoice_id}"
        )
