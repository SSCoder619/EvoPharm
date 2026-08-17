"""Domain exceptions for the Sales bounded context.

Every exception here is raised from inside a sales aggregate, entity, or value
object to protect a business invariant. None of them carry any dependency on
infrastructure or presentation concerns — translating a domain error into a UI
message or an API response is a job for an outer layer, not for the domain.
"""
from __future__ import annotations

from uuid import UUID


class SalesDomainError(Exception):
    """Base class for every error raised by the Sales domain."""


class InvalidSaleStateError(SalesDomainError):
    def __init__(self, sale_id: UUID, current_status: str, target_status: str) -> None:
        self.sale_id = sale_id
        self.current_status = current_status
        self.target_status = target_status
        super().__init__(
            f"Cannot transition sale {sale_id} from status "
            f"{current_status!r} to {target_status!r}"
        )


class InvalidSaleQuantityError(SalesDomainError):
    def __init__(self, value: object, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid sale quantity {value!r}: {reason}")


class InvalidSalePriceError(SalesDomainError):
    def __init__(self, value: object, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid sale price {value!r}: {reason}")


class InvalidSaleLineError(SalesDomainError):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid sale line: {reason}")


class DuplicateSaleLineError(SalesDomainError):
    def __init__(self, sale_id: UUID, medicine_id: UUID) -> None:
        self.sale_id = sale_id
        self.medicine_id = medicine_id
        super().__init__(
            f"Sale {sale_id} already contains a line for medicine {medicine_id}"
        )


class SaleLineNotFoundError(SalesDomainError):
    def __init__(self, sale_id: UUID, line_id: UUID) -> None:
        self.sale_id = sale_id
        self.line_id = line_id
        super().__init__(
            f"Sale line {line_id} not found in sale {sale_id}"
        )


class SaleAlreadyCancelledError(SalesDomainError):
    def __init__(self, sale_id: UUID) -> None:
        self.sale_id = sale_id
        super().__init__(f"Sale {sale_id} is already cancelled")


class SaleNotCancellableError(SalesDomainError):
    def __init__(self, sale_id: UUID, current_status: str, reason: str) -> None:
        self.sale_id = sale_id
        self.current_status = current_status
        self.reason = reason
        super().__init__(
            f"Sale {sale_id} in status {current_status!r} cannot be cancelled: {reason}"
        )


class ExceededSoldQuantityError(SalesDomainError):
    def __init__(self, line_id: UUID, sold: int, returning: int, previously_returned: int) -> None:
        self.line_id = line_id
        self.sold = sold
        self.returning = returning
        self.previously_returned = previously_returned
        super().__init__(
            f"Returning {returning} units would exceed sold quantity {sold} "
            f"for line {line_id} (already returned {previously_returned})"
        )


class ReceivingReturnAgainstCancelledSaleError(SalesDomainError):
    def __init__(self, sale_id: UUID) -> None:
        self.sale_id = sale_id
        super().__init__(
            f"Cannot process line return against cancelled sale {sale_id}"
        )


class InvalidCustomerReferenceError(SalesDomainError):
    def __init__(self, value: object, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid customer reference {value!r}: {reason}")


class InvalidInvoiceNumberError(SalesDomainError):
    def __init__(self, value: str, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid invoice number {value!r}: {reason}")


class InvalidPrescriptionReferenceError(SalesDomainError):
    def __init__(self, value: object, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid prescription reference {value!r}: {reason}")


class InvalidPaymentStateError(SalesDomainError):
    def __init__(self, sale_id: UUID, current_status: str, target_status: str) -> None:
        self.sale_id = sale_id
        self.current_status = current_status
        self.target_status = target_status
        super().__init__(
            f"Cannot transition payment for sale {sale_id} from "
            f"{current_status!r} to {target_status!r}"
        )
