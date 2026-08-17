"""Domain exceptions for the Supplier bounded context.

Every exception here is raised from inside a supplier aggregate, entity, or value
object to protect a business invariant. None of them carry any dependency on
infrastructure or presentation concerns — translating a domain error into a UI
message or an API response is a job for an outer layer, not for the domain.
"""
from __future__ import annotations

from uuid import UUID


class SupplierDomainError(Exception):
    """Base class for every error raised by the Supplier domain."""


class InvalidSupplierStateError(SupplierDomainError):
    def __init__(self, supplier_id: UUID, current_status: str, target_status: str) -> None:
        self.supplier_id = supplier_id
        self.current_status = current_status
        self.target_status = target_status
        super().__init__(
            f"Cannot transition supplier {supplier_id} from status "
            f"{current_status!r} to {target_status!r}"
        )


class InvalidSupplierNameError(SupplierDomainError):
    def __init__(self, value: str, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid supplier name {value!r}: {reason}")


class InvalidSupplierCodeError(SupplierDomainError):
    def __init__(self, value: str, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid supplier code {value!r}: {reason}")


class InvalidPhoneNumberError(SupplierDomainError):
    def __init__(self, value: str, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid phone number {value!r}: {reason}")


class InvalidEmailAddressError(SupplierDomainError):
    def __init__(self, value: str, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid email address {value!r}: {reason}")


class InvalidAddressError(SupplierDomainError):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid address: {reason}")


class InvalidGSTINError(SupplierDomainError):
    def __init__(self, value: str, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid GSTIN {value!r}: {reason}")


class InvalidPANError(SupplierDomainError):
    def __init__(self, value: str, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid PAN {value!r}: {reason}")


class SupplierAlreadyInactiveError(SupplierDomainError):
    def __init__(self, supplier_id: UUID) -> None:
        self.supplier_id = supplier_id
        super().__init__(f"Supplier {supplier_id} is already inactive")


class SupplierAlreadyActiveError(SupplierDomainError):
    def __init__(self, supplier_id: UUID) -> None:
        self.supplier_id = supplier_id
        super().__init__(f"Supplier {supplier_id} is already active")


class SupplierNotFoundError(SupplierDomainError):
    def __init__(self, supplier_id: UUID) -> None:
        self.supplier_id = supplier_id
        super().__init__(f"Supplier {supplier_id} not found")
