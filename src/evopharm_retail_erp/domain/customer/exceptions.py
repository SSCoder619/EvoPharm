"""Domain exceptions for the Customer bounded context.

Every exception here is raised from inside a customer aggregate, entity, or value
object to protect a business invariant. None of them carry any dependency on
infrastructure or presentation concerns — translating a domain error into a UI
message or an API response is a job for an outer layer, not for the domain.
"""
from __future__ import annotations

from uuid import UUID


class CustomerDomainError(Exception):
    """Base class for every error raised by the Customer domain."""


class InvalidCustomerStateError(CustomerDomainError):
    def __init__(self, customer_id: UUID, current_status: str, target_status: str) -> None:
        self.customer_id = customer_id
        self.current_status = current_status
        self.target_status = target_status
        super().__init__(
            f"Cannot transition customer {customer_id} from status "
            f"{current_status!r} to {target_status!r}"
        )


class InvalidCustomerNameError(CustomerDomainError):
    def __init__(self, value: str, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid customer name {value!r}: {reason}")


class InvalidCustomerCodeError(CustomerDomainError):
    def __init__(self, value: str, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid customer code {value!r}: {reason}")


class InvalidPhoneNumberError(CustomerDomainError):
    def __init__(self, value: str, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid phone number {value!r}: {reason}")


class InvalidEmailAddressError(CustomerDomainError):
    def __init__(self, value: str, reason: str) -> None:
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid email address {value!r}: {reason}")


class InvalidAddressError(CustomerDomainError):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid address: {reason}")


class CustomerAlreadyInactiveError(CustomerDomainError):
    def __init__(self, customer_id: UUID) -> None:
        self.customer_id = customer_id
        super().__init__(f"Customer {customer_id} is already inactive")


class CustomerAlreadyActiveError(CustomerDomainError):
    def __init__(self, customer_id: UUID) -> None:
        self.customer_id = customer_id
        super().__init__(f"Customer {customer_id} is already active")


class CustomerNotFoundError(CustomerDomainError):
    def __init__(self, customer_id: UUID) -> None:
        self.customer_id = customer_id
        super().__init__(f"Customer {customer_id} not found")
