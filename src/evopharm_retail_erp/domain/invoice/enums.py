"""Enum definitions for the Invoice bounded context.

Every enum here is used across invoice entities and value objects to represent a
finite set of valid billing document states, document types, tax classifications, and payment statuses.
None of them carry any dependency on infrastructure or presentation concerns —
translating enum values into UI labels or API responses is a job for an outer layer,
not for the domain.
"""
from __future__ import annotations

from enum import Enum, unique


@unique
class InvoiceStatus(str, Enum):
    """Lifecycle status of an Invoice aggregate root."""

    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    PAID = "PAID"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    CANCELLED = "CANCELLED"
    VOID = "VOID"


@unique
class InvoiceType(str, Enum):
    """Commercial document type classification."""

    TAX_INVOICE = "TAX_INVOICE"
    RETAIL_BILL = "RETAIL_BILL"
    CREDIT_NOTE = "CREDIT_NOTE"
    DEBIT_NOTE = "DEBIT_NOTE"


@unique
class TaxType(str, Enum):
    """GST tax classification based on place of supply."""

    INTRA_STATE = "INTRA_STATE"  # CGST + SGST (50% each)
    INTER_STATE = "INTER_STATE"  # IGST (100%)


@unique
class PaymentStatus(str, Enum):
    """Commercial payment settlement status of an invoice."""

    UNPAID = "UNPAID"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    REFUNDED = "REFUNDED"


@unique
class InvoiceLineStatus(str, Enum):
    """Fulfillment state of an individual invoice line item."""

    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
