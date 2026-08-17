"""Invoice domain package."""
from __future__ import annotations

# Entities
from .entities import Invoice, InvoiceLine

# Value Objects
from .value_objects import (
    CustomerReference,
    DiscountAmount,
    GstBreakdown,
    InvoiceId,
    InvoiceLineId,
    InvoiceNumber,
    InvoiceQuantity,
    InvoiceTotal,
    Money,
    SaleReference,
    TaxRate,
    UnitPrice,
)

# Enums
from .enums import (
    InvoiceLineStatus,
    InvoiceStatus,
    InvoiceType,
    PaymentStatus,
    TaxType,
)

# Exceptions
from .exceptions import (
    DuplicateInvoiceLineError,
    InvalidInvoiceAmountError,
    InvalidInvoiceLineError,
    InvalidInvoiceNumberError,
    InvalidInvoiceQuantityError,
    InvalidInvoiceStateError,
    InvalidPaymentStateError,
    InvalidTaxRateError,
    InvoiceAlreadyCancelledError,
    InvoiceDomainError,
    InvoiceLineNotFoundError,
    InvoiceNotCancellableError,
    OverpaymentError,
)

# Interfaces
from .interfaces import InvoiceRepository

# Specifications
from .specifications import (
    AndSpecification,
    CanCancelInvoiceSpecification,
    CanIssueInvoiceSpecification,
    HasOutstandingBalanceSpecification,
    IsCancelledInvoiceSpecification,
    IsDraftInvoiceSpecification,
    IsIssuedInvoiceSpecification,
    IsPaidInvoiceSpecification,
    IsPartiallyPaidInvoiceSpecification,
    NotSpecification,
    OrSpecification,
    Specification,
)

# Domain Events
from .domain_events import (
    InvoiceCancelled,
    InvoiceCreated,
    InvoiceDomainEvent,
    InvoiceIssued,
    InvoiceLineAdded,
    InvoiceLineRemoved,
    InvoicePaid,
    InvoicePartiallyPaid,
    InvoicePaymentRecorded,
)

# Services
from .services import InvoiceTaxCalculationService

__all__ = [
    "Invoice",
    "InvoiceLine",
    "CustomerReference",
    "DiscountAmount",
    "GstBreakdown",
    "InvoiceId",
    "InvoiceLineId",
    "InvoiceNumber",
    "InvoiceQuantity",
    "InvoiceTotal",
    "Money",
    "SaleReference",
    "TaxRate",
    "UnitPrice",
    "InvoiceLineStatus",
    "InvoiceStatus",
    "InvoiceType",
    "PaymentStatus",
    "TaxType",
    "DuplicateInvoiceLineError",
    "InvalidInvoiceAmountError",
    "InvalidInvoiceLineError",
    "InvalidInvoiceNumberError",
    "InvalidInvoiceQuantityError",
    "InvalidInvoiceStateError",
    "InvalidPaymentStateError",
    "InvalidTaxRateError",
    "InvoiceAlreadyCancelledError",
    "InvoiceDomainError",
    "InvoiceLineNotFoundError",
    "InvoiceNotCancellableError",
    "OverpaymentError",
    "InvoiceRepository",
    "AndSpecification",
    "CanCancelInvoiceSpecification",
    "CanIssueInvoiceSpecification",
    "HasOutstandingBalanceSpecification",
    "IsCancelledInvoiceSpecification",
    "IsDraftInvoiceSpecification",
    "IsIssuedInvoiceSpecification",
    "IsPaidInvoiceSpecification",
    "IsPartiallyPaidInvoiceSpecification",
    "NotSpecification",
    "OrSpecification",
    "Specification",
    "InvoiceCancelled",
    "InvoiceCreated",
    "InvoiceDomainEvent",
    "InvoiceIssued",
    "InvoiceLineAdded",
    "InvoiceLineRemoved",
    "InvoicePaid",
    "InvoicePartiallyPaid",
    "InvoicePaymentRecorded",
    "InvoiceTaxCalculationService",
]
