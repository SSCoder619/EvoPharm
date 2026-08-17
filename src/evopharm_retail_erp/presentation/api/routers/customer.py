"""Customer Profile API router."""
from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException

from evopharm_retail_erp.application.customer import (
    CustomerApplicationService,
    RegisterCustomerCommand,
    UpdateCustomerContactCommand,
)
from ..dependencies import get_customer_service
from ..schemas.customer import (
    CustomerResponse,
    RegisterCustomerRequest,
    UpdateCustomerContactRequest,
)

router = APIRouter(prefix="/api/v1/customers", tags=["Customer Management"])


@router.post("", response_model=CustomerResponse, status_code=201, summary="Register Customer")
async def register_customer(
    request: RegisterCustomerRequest,
    service: CustomerApplicationService = Depends(get_customer_service),
) -> CustomerResponse:
    """Register a new retail pharmacy customer profile."""
    cmd = RegisterCustomerCommand(
        name=request.name,
        phone=request.phone,
        email=request.email,
        street=request.address.street if request.address else None,
        city=request.address.city if request.address else None,
        state=request.address.state if request.address else None,
        pincode=request.address.postal_code if request.address else None,
    )
    result = await service.register_customer(cmd)
    res = result.value
    return CustomerResponse(
        id=res.customer_id,
        code=res.code,
        name=res.name,
        phone=res.phone,
        email=res.email,
        status=res.status,
        category=res.customer_type,
        version=res.version,
    )


@router.get("/{customer_id}", response_model=CustomerResponse, summary="Get Customer by ID")
async def get_customer_by_id(
    customer_id: UUID,
    service: CustomerApplicationService = Depends(get_customer_service),
) -> CustomerResponse:
    """Retrieve customer profile details by ID."""
    result = await service.get_customer(customer_id)
    res = result.value
    return CustomerResponse(
        id=res.customer_id,
        code=res.code,
        name=res.name,
        phone=res.phone,
        email=res.email,
        status=res.status,
        category=res.customer_type,
        version=res.version,
    )


@router.put("/{customer_id}/contact", response_model=CustomerResponse, summary="Update Contact Information")
async def update_contact_information(
    customer_id: UUID,
    request: UpdateCustomerContactRequest,
    service: CustomerApplicationService = Depends(get_customer_service),
) -> CustomerResponse:
    """Update customer phone number and email address."""
    cmd = UpdateCustomerContactCommand(
        customer_id=customer_id,
        phone=request.phone,
        email=request.email,
    )
    result = await service.update_contact_information(cmd)
    res = result.value
    return CustomerResponse(
        id=res.customer_id,
        code=res.code,
        name=res.name,
        phone=res.phone,
        email=res.email,
        status=res.status,
        category=res.customer_type,
        version=res.version,
    )
