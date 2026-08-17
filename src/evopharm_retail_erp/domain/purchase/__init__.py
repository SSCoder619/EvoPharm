"""Purchase domain package."""
from __future__ import annotations

# Entities
from .entities import Purchase, PurchaseLine

# Value Objects
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

# Enums
from .enums import (
    PaymentStatus,
    PurchaseLineStatus,
    PurchaseStatus,
    ReceivingStatus,
)

# Exceptions
from .exceptions import (
    DuplicatePurchaseLineError,
    ExceededOrderedQuantityError,
    InvalidInvoiceReferenceError,
    InvalidPaymentStateTransitionError,
    InvalidPurchaseLineError,
    InvalidPurchasePriceError,
    InvalidPurchaseQuantityError,
    InvalidPurchaseStateTransitionError,
    InvalidSupplierReferenceError,
    PurchaseAlreadyCancelledError,
    PurchaseDomainError,
    PurchaseLineNotFoundError,
    PurchaseNotCancellableError,
    ReceivingAgainstCancelledPurchaseError,
)

# Interfaces
from .interfaces import PurchaseRepository

# Specifications
from .specifications import (
    AndSpecification,
    CanCancelPurchaseSpecification,
    CanReceivePurchaseSpecification,
    HasOutstandingQuantitySpecification,
    IsPurchaseApprovedSpecification,
    IsPurchaseCancelledSpecification,
    IsPurchaseDraftSpecification,
    IsPurchaseOrderedSpecification,
    IsPurchaseReceivedSpecification,
    NotSpecification,
    OrSpecification,
    Specification,
)

# Domain Events
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

# Services
from .services import PurchasePricingService, VolumeDiscountRule

__all__ = [
    "Purchase",
    "PurchaseLine",
    "Discount",
    "InvoiceReference",
    "Money",
    "PurchaseId",
    "PurchaseLineId",
    "PurchaseOrderReference",
    "PurchaseQuantity",
    "PurchaseTotal",
    "SupplierReference",
    "TaxRate",
    "UnitPrice",
    "PaymentStatus",
    "PurchaseLineStatus",
    "PurchaseStatus",
    "ReceivingStatus",
    "DuplicatePurchaseLineError",
    "ExceededOrderedQuantityError",
    "InvalidInvoiceReferenceError",
    "InvalidPaymentStateTransitionError",
    "InvalidPurchaseLineError",
    "InvalidPurchasePriceError",
    "InvalidPurchaseQuantityError",
    "InvalidPurchaseStateTransitionError",
    "InvalidSupplierReferenceError",
    "PurchaseAlreadyCancelledError",
    "PurchaseDomainError",
    "PurchaseLineNotFoundError",
    "PurchaseNotCancellableError",
    "ReceivingAgainstCancelledPurchaseError",
    "PurchaseRepository",
    "AndSpecification",
    "CanCancelPurchaseSpecification",
    "CanReceivePurchaseSpecification",
    "HasOutstandingQuantitySpecification",
    "IsPurchaseApprovedSpecification",
    "IsPurchaseCancelledSpecification",
    "IsPurchaseDraftSpecification",
    "IsPurchaseOrderedSpecification",
    "IsPurchaseReceivedSpecification",
    "NotSpecification",
    "OrSpecification",
    "Specification",
    "PurchaseApproved",
    "PurchaseCancelled",
    "PurchaseCreated",
    "PurchaseDomainEvent",
    "PurchaseInvoiceAttached",
    "PurchaseLineAdded",
    "PurchaseLineRemoved",
    "PurchaseOrdered",
    "PurchasePartiallyReceived",
    "PurchasePaymentRecorded",
    "PurchaseReceived",
    "PurchasePricingService",
    "VolumeDiscountRule",
]
