"""Sales domain package."""
from __future__ import annotations

# Entities
from .entities import Sale, SaleLine

# Value Objects
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

# Enums
from .enums import (
    PaymentMethod,
    PaymentStatus,
    ReturnReason,
    SaleLineStatus,
    SaleStatus,
)

# Exceptions
from .exceptions import (
    DuplicateSaleLineError,
    ExceededSoldQuantityError,
    InvalidCustomerReferenceError,
    InvalidInvoiceNumberError,
    InvalidPaymentStateError,
    InvalidPrescriptionReferenceError,
    InvalidSaleLineError,
    InvalidSalePriceError,
    InvalidSaleQuantityError,
    InvalidSaleStateError,
    ReceivingReturnAgainstCancelledSaleError,
    SaleAlreadyCancelledError,
    SaleLineNotFoundError,
    SaleNotCancellableError,
    SalesDomainError,
)

# Interfaces
from .interfaces import SaleRepository

# Specifications
from .specifications import (
    AndSpecification,
    CanCancelSaleSpecification,
    CanConfirmSaleSpecification,
    HasOutstandingPaymentSpecification,
    HasReturnableQuantitySpecification,
    IsFullyPaidSpecification,
    IsSaleCancelledSpecification,
    IsSaleCompletedSpecification,
    IsSaleConfirmedSpecification,
    IsSaleDraftSpecification,
    NotSpecification,
    OrSpecification,
    Specification,
)

# Domain Events
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

# Services
from .services import PromotionalRule, SalesPromotionService

__all__ = [
    "Sale",
    "SaleLine",
    "CustomerReference",
    "Discount",
    "InvoiceNumber",
    "Money",
    "PaymentReference",
    "PrescriptionReference",
    "SaleId",
    "SaleLineId",
    "SaleQuantity",
    "SaleTotal",
    "TaxRate",
    "UnitPrice",
    "PaymentMethod",
    "PaymentStatus",
    "ReturnReason",
    "SaleLineStatus",
    "SaleStatus",
    "DuplicateSaleLineError",
    "ExceededSoldQuantityError",
    "InvalidCustomerReferenceError",
    "InvalidInvoiceNumberError",
    "InvalidPaymentStateError",
    "InvalidPrescriptionReferenceError",
    "InvalidSaleLineError",
    "InvalidSalePriceError",
    "InvalidSaleQuantityError",
    "InvalidSaleStateError",
    "ReceivingReturnAgainstCancelledSaleError",
    "SaleAlreadyCancelledError",
    "SaleLineNotFoundError",
    "SaleNotCancellableError",
    "SalesDomainError",
    "SaleRepository",
    "AndSpecification",
    "CanCancelSaleSpecification",
    "CanConfirmSaleSpecification",
    "HasOutstandingPaymentSpecification",
    "HasReturnableQuantitySpecification",
    "IsFullyPaidSpecification",
    "IsSaleCancelledSpecification",
    "IsSaleCompletedSpecification",
    "IsSaleConfirmedSpecification",
    "IsSaleDraftSpecification",
    "NotSpecification",
    "OrSpecification",
    "Specification",
    "PrescriptionAttached",
    "SaleCancelled",
    "SaleCompleted",
    "SaleConfirmed",
    "SaleCreated",
    "SaleLineAdded",
    "SaleLineRemoved",
    "SalePaymentRecorded",
    "SaleReturned",
    "SalesDomainEvent",
    "PromotionalRule",
    "SalesPromotionService",
]
