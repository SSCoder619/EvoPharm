"""Supplier / Vendor API router."""
from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException

from evopharm_retail_erp.application.supplier import (
    RegisterSupplierCommand,
    SupplierApplicationService,
    UpdateSupplierContactCommand,
)
from ..dependencies import get_supplier_service
from ..schemas.supplier import (
    RegisterSupplierRequest,
    SupplierResponse,
    UpdateSupplierContactRequest,
)

router = APIRouter(prefix="/api/v1/suppliers", tags=["Supplier Management"])


@router.post("", response_model=SupplierResponse, status_code=201, summary="Register Supplier")
async def register_supplier(
    request: RegisterSupplierRequest,
    service: SupplierApplicationService = Depends(get_supplier_service),
) -> SupplierResponse:
    """Register a new pharmaceutical supplier/vendor profile."""
    cmd = RegisterSupplierCommand(
        name=request.name,
        phone=request.phone,
        code=request.code,
        email=request.email,
        gstin=request.gstin,
        pan=request.pan,
        category=request.category,
    )
    result = await service.register_supplier(cmd)
    res = result.value
    return SupplierResponse(
        id=res.supplier_id,
        code=res.code,
        name=res.name,
        phone=res.phone,
        email=res.email,
        gstin=res.gstin,
        pan=res.pan,
        status=res.status,
        category=res.category,
        version=res.version,
    )


@router.get("/{supplier_id}", response_model=SupplierResponse, summary="Get Supplier by ID")
async def get_supplier_by_id(
    supplier_id: UUID,
    service: SupplierApplicationService = Depends(get_supplier_service),
) -> SupplierResponse:
    """Retrieve supplier profile details by ID."""
    result = await service.get_supplier(supplier_id)
    res = result.value
    return SupplierResponse(
        id=res.supplier_id,
        code=res.code,
        name=res.name,
        phone=res.phone,
        email=res.email,
        gstin=res.gstin,
        pan=res.pan,
        status=res.status,
        category=res.category,
        version=res.version,
    )


@router.put("/{supplier_id}/contact", response_model=SupplierResponse, summary="Update Contact Information")
async def update_contact_information(
    supplier_id: UUID,
    request: UpdateSupplierContactRequest,
    service: SupplierApplicationService = Depends(get_supplier_service),
) -> SupplierResponse:
    """Update supplier contact phone number and email address."""
    cmd = UpdateSupplierContactCommand(
        supplier_id=supplier_id,
        phone=request.phone,
        email=request.email,
    )
    result = await service.update_contact_information(cmd)
    res = result.value
    return SupplierResponse(
        id=res.supplier_id,
        code=res.code,
        name=res.name,
        phone=res.phone,
        email=res.email,
        gstin=res.gstin,
        pan=res.pan,
        status=res.status,
        category=res.category,
        version=res.version,
    )
