"""API request and response schemas for Customer bounded context."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AddressSchema(BaseModel):
    street: str = Field(..., description="Street address line")
    city: str = Field(..., description="City name")
    state: str = Field(..., description="State name")
    postal_code: str = Field(..., description="PIN / Postal Code")
    country: str = Field(default="India", description="Country name")


class RegisterCustomerRequest(BaseModel):
    name: str = Field(..., description="Customer full name")
    phone: str = Field(..., description="Contact phone number")
    email: Optional[str] = Field(default=None, description="Contact email address")
    address: Optional[AddressSchema] = Field(default=None, description="Address details")
    patient_id: Optional[str] = Field(default=None, description="Optional patient registration ID")


class UpdateCustomerContactRequest(BaseModel):
    phone: str = Field(..., description="Updated phone number")
    email: Optional[str] = Field(default=None, description="Updated email address")


class CustomerResponse(BaseModel):
    id: UUID = Field(..., description="Unique Customer ID")
    code: str = Field(..., description="Unique Customer code")
    name: str = Field(..., description="Customer name")
    phone: str = Field(..., description="Contact phone number")
    email: Optional[str] = Field(default=None, description="Contact email address")
    status: str = Field(..., description="Account status")
    category: str = Field(..., description="Customer classification category")
    version: int = Field(..., description="Optimistic concurrency version")
