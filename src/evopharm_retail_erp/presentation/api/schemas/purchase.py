"""API request and response schemas for Purchase bounded context."""
from __future__ import annotations

from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CreatePurchaseRequest(BaseModel):
    supplier_id: UUID = Field(..., description="Supplier ID")
    order_reference: str = Field(..., description="Purchase order reference number (e.g. PO-2026-0001)")
    supplier_code: Optional[str] = Field(default=None, description="Supplier code")
    supplier_name: Optional[str] = Field(default=None, description="Supplier name")
    invoice_reference: Optional[str] = Field(default=None, description="Commercial invoice reference number")


class AddPurchaseLineRequest(BaseModel):
    medicine_id: UUID = Field(..., description="Medicine product ID")
    ordered_quantity: int = Field(..., gt=0, description="Quantity ordered")
    unit_price: Decimal = Field(..., gt=0, description="Unit purchase price")
    discount_percentage: Decimal = Field(default=Decimal("0.00"), ge=0, le=100, description="Discount percentage")
    tax_rate_percentage: Decimal = Field(default=Decimal("0.00"), ge=0, le=100, description="GST / Tax percentage")


class ReceivePurchaseStockRequest(BaseModel):
    line_id: UUID = Field(..., description="Purchase line ID")
    quantity: int = Field(..., gt=0, description="Quantity received")
    batch_number: str = Field(..., description="Manufacturer batch number")


class PurchaseLineResponse(BaseModel):
    id: UUID = Field(..., description="Line item ID")
    medicine_id: UUID = Field(..., description="Medicine product ID")
    ordered_quantity: int = Field(..., description="Ordered quantity")
    received_quantity: int = Field(..., description="Received quantity")
    unit_price: Decimal = Field(..., description="Unit price amount")
    status: str = Field(..., description="Line status")


class PurchaseResponse(BaseModel):
    id: UUID = Field(..., description="Purchase order ID")
    order_reference: str = Field(..., description="Purchase order reference number")
    invoice_reference: Optional[str] = Field(default=None, description="Invoice reference number")
    supplier_id: UUID = Field(..., description="Supplier ID")
    purchase_status: str = Field(..., description="Purchase lifecycle status")
    receiving_status: str = Field(..., description="Receiving status")
    payment_status: str = Field(..., description="Payment status")
    lines: List[PurchaseLineResponse] = Field(default_factory=list, description="Purchase line items")
    version: int = Field(..., description="Optimistic concurrency version")
