"""API request and response schemas for Medicine bounded context."""
from __future__ import annotations

from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CompositionItemSchema(BaseModel):
    ingredient: str = Field(..., description="Active pharmaceutical ingredient name")
    strength: Decimal = Field(..., description="Strength amount")
    unit: str = Field(default="MG", description="Strength unit (MG, G, ML, IU, etc.)")


class RegisterMedicineRequest(BaseModel):
    name: str = Field(..., description="Medicine brand name")
    generic_name: str = Field(..., description="Non-proprietary generic classification name")
    composition: List[CompositionItemSchema] = Field(..., description="Active ingredient composition items")
    manufacturer: str = Field(..., description="Manufacturer brand name")
    dosage_form: str = Field(default="TABLET", description="Dosage form (TABLET, CAPSULE, SYRUP, etc.)")
    pack_size: int = Field(default=10, description="Base dispensing units per pack")
    unit_of_measure: str = Field(default="TABLET", description="Unit of measure")
    hsn_code: str = Field(default="300490", description="Indian HSN code")
    schedule: str = Field(default="UNSCHEDULED", description="Drug classification schedule")
    barcodes: List[str] = Field(default_factory=list, description="Barcodes")
    alternate_names: List[str] = Field(default_factory=list, description="Brand alternate names")
    storage_condition: Optional[str] = Field(default=None, description="Storage instructions")


class MedicineResponse(BaseModel):
    id: UUID = Field(..., description="Unique Medicine ID")
    name: str = Field(..., description="Brand name")
    generic_name: str = Field(..., description="Generic name")
    manufacturer: str = Field(..., description="Manufacturer")
    hsn_code: str = Field(..., description="HSN classification code")
    dosage_form: str = Field(..., description="Dosage form")
    schedule: str = Field(..., description="Schedule classification")
    status: str = Field(..., description="Medicine lifecycle status")
    version: int = Field(..., description="Optimistic concurrency version")
