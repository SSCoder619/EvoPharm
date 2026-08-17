"""Supplier domain package."""
from __future__ import annotations

# Entities
from .entities import Supplier

# Value Objects
from .value_objects import (
    GSTIN,
    PAN,
    Address,
    EmailAddress,
    PhoneNumber,
    PostalCode,
    SupplierCode,
    SupplierId,
    SupplierName,
)

# Enums
from .enums import SupplierCategory, SupplierStatus

# Exceptions
from .exceptions import (
    InvalidAddressError,
    InvalidEmailAddressError,
    InvalidGSTINError,
    InvalidPANError,
    InvalidPhoneNumberError,
    InvalidSupplierCodeError,
    InvalidSupplierNameError,
    InvalidSupplierStateError,
    SupplierAlreadyActiveError,
    SupplierAlreadyInactiveError,
    SupplierDomainError,
    SupplierNotFoundError,
)

# Interfaces
from .interfaces import SupplierRepository

# Specifications
from .specifications import (
    AndSpecification,
    CanDeactivateSupplierSpecification,
    CanPurchaseFromSupplierSpecification,
    HasValidTaxRegistrationSpecification,
    IsActiveSupplierSpecification,
    IsInactiveSupplierSpecification,
    IsSuspendedSupplierSpecification,
    NotSpecification,
    OrSpecification,
    Specification,
)

# Domain Events
from .domain_events import (
    SupplierActivated,
    SupplierAddressUpdated,
    SupplierArchived,
    SupplierComplianceUpdated,
    SupplierContactUpdated,
    SupplierDeactivated,
    SupplierDetailsUpdated,
    SupplierDomainEvent,
    SupplierReactivated,
    SupplierRegistered,
    SupplierSuspended,
)

# Services
from .services import SupplierEvaluationService

__all__ = [
    "Supplier",
    "GSTIN",
    "PAN",
    "Address",
    "EmailAddress",
    "PhoneNumber",
    "PostalCode",
    "SupplierCode",
    "SupplierId",
    "SupplierName",
    "SupplierCategory",
    "SupplierStatus",
    "InvalidAddressError",
    "InvalidEmailAddressError",
    "InvalidGSTINError",
    "InvalidPANError",
    "InvalidPhoneNumberError",
    "InvalidSupplierCodeError",
    "InvalidSupplierNameError",
    "InvalidSupplierStateError",
    "SupplierAlreadyActiveError",
    "SupplierAlreadyInactiveError",
    "SupplierDomainError",
    "SupplierNotFoundError",
    "SupplierRepository",
    "AndSpecification",
    "CanDeactivateSupplierSpecification",
    "CanPurchaseFromSupplierSpecification",
    "HasValidTaxRegistrationSpecification",
    "IsActiveSupplierSpecification",
    "IsInactiveSupplierSpecification",
    "IsSuspendedSupplierSpecification",
    "NotSpecification",
    "OrSpecification",
    "Specification",
    "SupplierActivated",
    "SupplierAddressUpdated",
    "SupplierArchived",
    "SupplierComplianceUpdated",
    "SupplierContactUpdated",
    "SupplierDeactivated",
    "SupplierDetailsUpdated",
    "SupplierDomainEvent",
    "SupplierReactivated",
    "SupplierRegistered",
    "SupplierSuspended",
    "SupplierEvaluationService",
]
