"""API request and response schemas for Sales bounded context."""
from __future__ import annotations

from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CreateSaleRequest(BaseModel):
    customer_id: Optional[UUID] = Field(default=None, description="Optional Customer ID")
    prescription_reference: Optional[str] = Field(default=None, description="Optional prescription reference number")


class AddSaleLineRequest(BaseModel):
    medicine_id: UUID = Field(..., description="Medicine product ID")
    medicine_batch_id: UUID = Field(..., description="Medicine batch ID")
    inventory_id: UUID = Field(..., description="Inventory projection ID")
    quantity: int = Field(..., gt=0, description="Quantity dispensed")
    unit_price: Decimal = Field(..., gt=0, description="Dispensing unit price")
    discount_percentage: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    tax_rate_percentage: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)


class SaleLineResponse(BaseModel):
    id: UUID = Field(..., description="Sale line item ID")
    medicine_id: UUID = Field(..., description="Medicine product ID")
    medicine_batch_id: UUID = Field(..., description="Medicine batch ID")
    quantity: int = Field(..., description="Dispensed quantity")
    unit_price: Decimal = Field(..., description="Unit price amount")
    line_total: Decimal = Field(..., description="Net line total amount")


class SaleResponse(BaseModel):
    id: UUID = Field(..., description="Sale transaction ID")
    receipt_number: str = Field(..., description="Receipt reference number")
    customer_id: Optional[UUID] = Field(default=None, description="Customer ID")
    status: str = Field(..., description="Sale status")
    total_amount: Decimal = Field(..., description="Net total sale amount")
    lines: List[SaleLineResponse] = Field(default_factory=list, description="Sale line items")
    version: int = Field(..., description="Optimistic concurrency version")
