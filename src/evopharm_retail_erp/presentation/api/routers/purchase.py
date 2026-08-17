"""Purchase Procurement API router."""
from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException

from evopharm_retail_erp.application.purchase import (
    AddPurchaseLineCommand,
    ApprovePurchaseCommand,
    CreatePurchaseCommand,
    PurchaseApplicationService,
)
from evopharm_retail_erp.application.common import UnitOfWork
from evopharm_retail_erp.domain.purchase import PurchaseId
from ..dependencies import get_purchase_service, get_uow
from ..schemas.purchase import (
    AddPurchaseLineRequest,
    CreatePurchaseRequest,
    PurchaseLineResponse,
    PurchaseResponse,
    ReceivePurchaseStockRequest,
)

router = APIRouter(prefix="/api/v1/purchases", tags=["Purchase Procurement"])


@router.post("", response_model=PurchaseResponse, status_code=201, summary="Create Purchase Order")
async def create_purchase(
    request: CreatePurchaseRequest,
    service: PurchaseApplicationService = Depends(get_purchase_service),
) -> PurchaseResponse:
    """Initialize a new draft purchase order."""
    cmd = CreatePurchaseCommand(
        supplier_id=request.supplier_id,
        order_reference=request.order_reference,
    )
    result = await service.create_purchase(cmd)
    res = result.value
    return _build_purchase_response(res)


@router.post("/{purchase_id}/lines", response_model=PurchaseResponse, summary="Add Purchase Line")
async def add_purchase_line(
    purchase_id: UUID,
    request: AddPurchaseLineRequest,
    service: PurchaseApplicationService = Depends(get_purchase_service),
) -> PurchaseResponse:
    """Add a line item item to a draft purchase order."""
    cmd = AddPurchaseLineCommand(
        purchase_id=purchase_id,
        medicine_id=request.medicine_id,
        ordered_quantity=request.ordered_quantity,
        unit_price=request.unit_price,
        discount_percentage=request.discount_percentage,
        tax_rate_percentage=request.tax_rate_percentage,
    )
    result = await service.add_line(cmd)
    res = result.value
    return _build_purchase_response(res)


@router.post("/{purchase_id}/approve", response_model=PurchaseResponse, summary="Approve Purchase Order")
async def approve_purchase(
    purchase_id: UUID,
    service: PurchaseApplicationService = Depends(get_purchase_service),
) -> PurchaseResponse:
    """Approve a draft purchase order for ordering."""
    cmd = ApprovePurchaseCommand(purchase_id=purchase_id)
    result = await service.approve_purchase(cmd)
    res = result.value
    return _build_purchase_response(res)


@router.get("/{purchase_id}", response_model=PurchaseResponse, summary="Get Purchase Order by ID")
async def get_purchase_by_id(
    purchase_id: UUID,
    uow: UnitOfWork = Depends(get_uow),
) -> PurchaseResponse:
    """Retrieve purchase order details by ID."""
    async with uow as active_uow:
        purchase = active_uow.purchases.get_by_id(PurchaseId(purchase_id))
        if purchase is None:
            raise HTTPException(status_code=404, detail=f"Purchase {purchase_id} not found")

        from evopharm_retail_erp.application.purchase.results import PurchaseResult
        res = PurchaseResult.from_domain(purchase)
        return _build_purchase_response(res)


def _build_purchase_response(res) -> PurchaseResponse:
    sup_id: UUID
    if isinstance(res.supplier_id, UUID):
        sup_id = res.supplier_id
    else:
        sup_id = UUID(str(res.supplier_id))

    lines = []
    for line in res.lines:
        u_price = line.unit_price.amount if hasattr(line.unit_price, "amount") else line.unit_price
        lines.append(
            PurchaseLineResponse(
                id=line.line_id,
                medicine_id=line.medicine_id,
                ordered_quantity=line.ordered_quantity,
                received_quantity=line.received_quantity,
                unit_price=u_price,
                status=line.status,
            )
        )

    return PurchaseResponse(
        id=res.purchase_id,
        order_reference=res.order_reference,
        invoice_reference=res.invoice_reference,
        supplier_id=sup_id,
        purchase_status=res.purchase_status,
        receiving_status=res.receiving_status,
        payment_status=res.payment_status,
        lines=lines,
        version=res.version,
    )
