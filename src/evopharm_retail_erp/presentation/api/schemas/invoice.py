"""API request and response schemas for Invoice bounded context."""
from __future__ import annotations

from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CreateInvoiceRequest(BaseModel):
    source_document_type: str = Field(..., description="Source document type (SALE, PURCHASE_ORDER, etc.)")
    source_document_id: UUID = Field(..., description="Source document ID")
    customer_id: Optional[UUID] = Field(default=None, description="Optional Customer ID")
    supplier_id: Optional[UUID] = Field(default=None, description="Optional Supplier ID")
    due_days: int = Field(default=30, ge=0, description="Payment credit period days")


class RecordPaymentRequest(BaseModel):
    payment_amount: Decimal = Field(..., gt=0, description="Monetary payment settlement amount")
    payment_method: str = Field(default="CASH", description="Payment method (CASH, UPI, CARD, BANK_TRANSFER)")
    reference_number: Optional[str] = Field(default=None, description="Transaction reference number")


class InvoiceResponse(BaseModel):
    id: UUID = Field(..., description="Unique Invoice ID")
    invoice_number: str = Field(..., description="Unique Commercial Invoice Number")
    total_amount: Decimal = Field(..., description="Total invoice amount")
    paid_amount: Decimal = Field(..., description="Total paid amount")
    status: str = Field(..., description="Invoice payment status")
    version: int = Field(..., description="Optimistic concurrency version")
