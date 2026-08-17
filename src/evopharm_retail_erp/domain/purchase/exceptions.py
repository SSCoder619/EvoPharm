"""Domain exceptions for the Purchase bounded context.

Every exception here is raised from inside a purchase aggregate, entity, or value
object to protect a business invariant. None of them carry any dependency on
infrastructure or presentation concerns — translating a domain error into a UI
message or an API response is a job for an outer layer, not for the domain.
"""
from __future__ import annotations

from uuid import UUID


class PurchaseDomainError(Exception):
    """Base class for every error raised by the Purchase domain."""


class InvalidPurchaseStateTransitionError(PurchaseDomainError):
    def __init__(self, purchase_id: UUID, current_status: str, target_status: str) -> None:
        self.purchase_id = purchase_id
        self.current_status = current_status
        self.target_status = target_status
        super().__init__(
            f"Cannot transition purchase {purchase_id} from status "
            f"{current_status!r} to {target_status!r}"
        )


class InvalidPurchaseQuantityError(PurchaseDomainError):
    def __init__(self, value: object, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid purchase quantity {value!r}: {reason}")


class InvalidPurchasePriceError(PurchaseDomainError):
    def __init__(self, value: object, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid purchase price {value!r}: {reason}")


class InvalidPurchaseLineError(PurchaseDomainError):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid purchase line: {reason}")


class DuplicatePurchaseLineError(PurchaseDomainError):
    def __init__(self, purchase_id: UUID, medicine_id: UUID) -> None:
        self.purchase_id = purchase_id
        self.medicine_id = medicine_id
        super().__init__(
            f"Purchase {purchase_id} already contains a line for medicine {medicine_id}"
        )


class PurchaseLineNotFoundError(PurchaseDomainError):
    def __init__(self, purchase_id: UUID, line_id: UUID) -> None:
        self.purchase_id = purchase_id
        self.line_id = line_id
        super().__init__(
            f"Purchase line {line_id} not found in purchase {purchase_id}"
        )


class PurchaseAlreadyCancelledError(PurchaseDomainError):
    def __init__(self, purchase_id: UUID) -> None:
        self.purchase_id = purchase_id
        super().__init__(f"Purchase {purchase_id} is already cancelled")


class PurchaseNotCancellableError(PurchaseDomainError):
    def __init__(self, purchase_id: UUID, current_status: str, reason: str) -> None:
        self.purchase_id = purchase_id
        self.current_status = current_status
        self.reason = reason
        super().__init__(
            f"Purchase {purchase_id} in status {current_status!r} cannot be cancelled: {reason}"
        )


class ExceededOrderedQuantityError(PurchaseDomainError):
    def __init__(self, line_id: UUID, ordered: int, receiving: int, previously_received: int) -> None:
        self.line_id = line_id
        self.ordered = ordered
        self.receiving = receiving
        self.previously_received = previously_received
        super().__init__(
            f"Receiving {receiving} units would exceed ordered quantity {ordered} "
            f"for line {line_id} (already received {previously_received})"
        )


class ReceivingAgainstCancelledPurchaseError(PurchaseDomainError):
    def __init__(self, purchase_id: UUID) -> None:
        self.purchase_id = purchase_id
        super().__init__(
            f"Cannot receive stock against cancelled purchase {purchase_id}"
        )


class InvalidInvoiceReferenceError(PurchaseDomainError):
    def __init__(self, value: str, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid invoice reference {value!r}: {reason}")


class InvalidSupplierReferenceError(PurchaseDomainError):
    def __init__(self, value: object, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid supplier reference {value!r}: {reason}")


class InvalidPaymentStateTransitionError(PurchaseDomainError):
    def __init__(self, purchase_id: UUID, current_status: str, target_status: str) -> None:
        self.purchase_id = purchase_id
        self.current_status = current_status
        self.target_status = target_status
        super().__init__(
            f"Cannot transition payment for purchase {purchase_id} from "
            f"{current_status!r} to {target_status!r}"
        )
