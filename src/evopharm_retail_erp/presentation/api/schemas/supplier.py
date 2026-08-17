"""API request and response schemas for Supplier bounded context."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RegisterSupplierRequest(BaseModel):
    name: str = Field(..., description="Supplier business name")
    phone: str = Field(..., description="Contact phone number")
    code: Optional[str] = Field(default=None, description="Unique supplier code")
    email: Optional[str] = Field(default=None, description="Contact email address")
    gstin: Optional[str] = Field(default=None, description="15-character Indian GSTIN")
    pan: Optional[str] = Field(default=None, description="10-character Indian PAN")
    category: str = Field(default="DISTRIBUTOR", description="Supplier category (DISTRIBUTOR, MANUFACTURER, etc.)")


class UpdateSupplierContactRequest(BaseModel):
    phone: str = Field(..., description="Updated phone number")
    email: Optional[str] = Field(default=None, description="Updated email address")


class SupplierResponse(BaseModel):
    id: UUID = Field(..., description="Unique Supplier ID")
    code: str = Field(..., description="Supplier code")
    name: str = Field(..., description="Supplier business name")
    phone: str = Field(..., description="Contact phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    gstin: Optional[str] = Field(default=None, description="GSTIN compliance identifier")
    pan: Optional[str] = Field(default=None, description="PAN compliance identifier")
    status: str = Field(..., description="Supplier status")
    category: str = Field(..., description="Category")
    version: int = Field(..., description="Optimistic concurrency version")
