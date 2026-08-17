"""Inventory Management API router."""
from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException

from evopharm_retail_erp.application.inventory import (
    DispenseStockCommand,
    InventoryApplicationService,
    ReceiveStockCommand,
    ReleaseStockCommand,
    ReserveStockCommand,
)
from evopharm_retail_erp.application.common import UnitOfWork
from evopharm_retail_erp.domain.inventory import InventoryId
from ..dependencies import get_inventory_service, get_uow
from ..schemas.inventory import (
    DispenseStockRequest,
    InventoryResponse,
    ReceiveStockRequest,
    ReleaseStockRequest,
    ReserveStockRequest,
)

router = APIRouter(prefix="/api/v1/inventory", tags=["Inventory Control"])


@router.post("/receive", response_model=InventoryResponse, summary="Receive Stock")
async def receive_stock(
    request: ReceiveStockRequest,
    service: InventoryApplicationService = Depends(get_inventory_service),
) -> InventoryResponse:
    """Receive physical stock units into inventory."""
    cmd = ReceiveStockCommand(
        medicine_id=request.medicine_id,
        medicine_batch_id=request.medicine_batch_id,
        quantity=request.quantity,
        inventory_id=request.inventory_id,
        document_type=request.document_type,
        document_id=request.document_id,
        reference_number=request.reference_number,
        reason=request.reason,
    )
    result = await service.receive_stock(cmd)
    res = result.value
    return InventoryResponse(
        id=res.inventory_id,
        medicine_id=res.medicine_id,
        medicine_batch_id=res.medicine_batch_id,
        quantity_on_hand=res.quantity_on_hand,
        quantity_reserved=res.quantity_reserved,
        quantity_available=res.quantity_available,
        status=res.status,
        version=res.version,
    )


@router.post("/reserve", response_model=InventoryResponse, summary="Reserve Stock")
async def reserve_stock(
    request: ReserveStockRequest,
    service: InventoryApplicationService = Depends(get_inventory_service),
) -> InventoryResponse:
    """Hold stock units in reserved status."""
    cmd = ReserveStockCommand(
        inventory_id=request.inventory_id,
        quantity=request.quantity,
    )
    result = await service.reserve_stock(cmd)
    res = result.value
    return InventoryResponse(
        id=res.inventory_id,
        medicine_id=res.medicine_id,
        medicine_batch_id=res.medicine_batch_id,
        quantity_on_hand=res.quantity_on_hand,
        quantity_reserved=res.quantity_reserved,
        quantity_available=res.quantity_available,
        status=res.status,
        version=res.version,
    )


@router.post("/release", response_model=InventoryResponse, summary="Release Reservation")
async def release_stock(
    request: ReleaseStockRequest,
    service: InventoryApplicationService = Depends(get_inventory_service),
) -> InventoryResponse:
    """Release reserved stock back to available pool."""
    cmd = ReleaseStockCommand(
        inventory_id=request.inventory_id,
        quantity=request.quantity,
    )
    result = await service.release_stock(cmd)
    res = result.value
    return InventoryResponse(
        id=res.inventory_id,
        medicine_id=res.medicine_id,
        medicine_batch_id=res.medicine_batch_id,
        quantity_on_hand=res.quantity_on_hand,
        quantity_reserved=res.quantity_reserved,
        quantity_available=res.quantity_available,
        status=res.status,
        version=res.version,
    )


@router.post("/dispense", response_model=InventoryResponse, summary="Dispense Stock")
async def dispense_stock(
    request: DispenseStockRequest,
    service: InventoryApplicationService = Depends(get_inventory_service),
) -> InventoryResponse:
    """Dispense stock units for a sale."""
    cmd = DispenseStockCommand(
        inventory_id=request.inventory_id,
        quantity=request.quantity,
        document_type=request.document_type,
        document_id=request.document_id,
        reference_number=request.reference_number,
        reason=request.reason,
    )
    result = await service.dispense_stock(cmd)
    res = result.value
    return InventoryResponse(
        id=res.inventory_id,
        medicine_id=res.medicine_id,
        medicine_batch_id=res.medicine_batch_id,
        quantity_on_hand=res.quantity_on_hand,
        quantity_reserved=res.quantity_reserved,
        quantity_available=res.quantity_available,
        status=res.status,
        version=res.version,
    )


@router.get("/{inventory_id}", response_model=InventoryResponse, summary="Get Inventory by ID")
async def get_inventory_by_id(
    inventory_id: UUID,
    uow: UnitOfWork = Depends(get_uow),
) -> InventoryResponse:
    """Retrieve inventory projection by ID."""
    async with uow as active_uow:
        inv = active_uow.inventory.get_by_id(InventoryId(inventory_id))
        if inv is None:
            raise HTTPException(status_code=404, detail=f"Inventory {inventory_id} not found")

        return InventoryResponse(
            id=inv.id.value,
            medicine_id=inv.medicine_id.value,
            medicine_batch_id=inv.medicine_batch_id.value,
            quantity_on_hand=inv.quantity_on_hand.value,
            quantity_reserved=inv.quantity_reserved.value,
            quantity_available=inv.quantity_available.value,
            status=inv.status.value,
            version=inv.version,
        )
