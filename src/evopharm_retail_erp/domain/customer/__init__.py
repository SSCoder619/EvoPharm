"""Customer domain package."""
from __future__ import annotations

# Entities
from .entities import Customer

# Value Objects
from .value_objects import (
    Address,
    CustomerCode,
    CustomerId,
    CustomerName,
    EmailAddress,
    PhoneNumber,
    PostalCode,
)

# Enums
from .enums import CustomerStatus, CustomerType

# Exceptions
from .exceptions import (
    CustomerAlreadyActiveError,
    CustomerAlreadyInactiveError,
    CustomerDomainError,
    CustomerNotFoundError,
    InvalidAddressError,
    InvalidCustomerCodeError,
    InvalidCustomerNameError,
    InvalidCustomerStateError,
    InvalidEmailAddressError,
    InvalidPhoneNumberError,
)

# Interfaces
from .interfaces import CustomerRepository

# Specifications
from .specifications import (
    AndSpecification,
    CanDeactivateCustomerSpecification,
    CanUpdateCustomerSpecification,
    HasValidContactInformationSpecification,
    IsActiveCustomerSpecification,
    IsInactiveCustomerSpecification,
    NotSpecification,
    OrSpecification,
    Specification,
)

# Domain Events
from .domain_events import (
    CustomerActivated,
    CustomerAddressUpdated,
    CustomerContactUpdated,
    CustomerDeactivated,
    CustomerDomainEvent,
    CustomerProfileUpdated,
    CustomerRegistered,
    CustomerSuspended,
)

# Services
from .services import CustomerEligibilityService

__all__ = [
    "Customer",
    "Address",
    "CustomerCode",
    "CustomerId",
    "CustomerName",
    "EmailAddress",
    "PhoneNumber",
    "PostalCode",
    "CustomerStatus",
    "CustomerType",
    "CustomerAlreadyActiveError",
    "CustomerAlreadyInactiveError",
    "CustomerDomainError",
    "CustomerNotFoundError",
    "InvalidAddressError",
    "InvalidCustomerCodeError",
    "InvalidCustomerNameError",
    "InvalidCustomerStateError",
    "InvalidEmailAddressError",
    "InvalidPhoneNumberError",
    "CustomerRepository",
    "AndSpecification",
    "CanDeactivateCustomerSpecification",
    "CanUpdateCustomerSpecification",
    "HasValidContactInformationSpecification",
    "IsActiveCustomerSpecification",
    "IsInactiveCustomerSpecification",
    "NotSpecification",
    "OrSpecification",
    "Specification",
    "CustomerActivated",
    "CustomerAddressUpdated",
    "CustomerContactUpdated",
    "CustomerDeactivated",
    "CustomerDomainEvent",
    "CustomerProfileUpdated",
    "CustomerRegistered",
    "CustomerSuspended",
    "CustomerEligibilityService",
]
