"""API request and response schemas for Inventory bounded context."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ReceiveStockRequest(BaseModel):
    medicine_id: UUID = Field(..., description="Medicine product ID")
    medicine_batch_id: UUID = Field(..., description="Medicine batch ID")
    quantity: int = Field(..., gt=0, description="Quantity of units received")
    inventory_id: Optional[UUID] = Field(default=None, description="Optional existing inventory ID")
    document_type: Optional[str] = Field(default=None, description="Source document type")
    document_id: Optional[UUID] = Field(default=None, description="Source document ID")
    reference_number: Optional[str] = Field(default=None, description="Source document reference number")
    reason: Optional[str] = Field(default=None, description="Operational movement reason")


class ReserveStockRequest(BaseModel):
    inventory_id: UUID = Field(..., description="Inventory projection ID")
    quantity: int = Field(..., gt=0, description="Quantity to hold in reservation")


class ReleaseStockRequest(BaseModel):
    inventory_id: UUID = Field(..., description="Inventory projection ID")
    quantity: int = Field(..., gt=0, description="Quantity to release back to available stock")


class DispenseStockRequest(BaseModel):
    inventory_id: UUID = Field(..., description="Inventory projection ID")
    quantity: int = Field(..., gt=0, description="Quantity to dispense for a sale")
    document_type: Optional[str] = Field(default=None, description="Source document type")
    document_id: Optional[UUID] = Field(default=None, description="Source document ID")
    reference_number: Optional[str] = Field(default=None, description="Source document reference number")
    reason: Optional[str] = Field(default=None, description="Operational movement reason")


class InventoryResponse(BaseModel):
    id: UUID = Field(..., description="Inventory projection ID")
    medicine_id: UUID = Field(..., description="Medicine product ID")
    medicine_batch_id: UUID = Field(..., description="Medicine batch ID")
    quantity_on_hand: int = Field(..., description="Total quantity physical stock on hand")
    quantity_reserved: int = Field(..., description="Quantity held in reservation")
    quantity_available: int = Field(..., description="Quantity available for dispensing")
    status: str = Field(..., description="Stock level status")
    version: int = Field(..., description="Optimistic concurrency version")
