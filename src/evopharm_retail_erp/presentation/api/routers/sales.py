"""Sales Point of Sale (POS) API router."""
from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException

from evopharm_retail_erp.application.sales import (
    AddSaleLineCommand,
    CompleteSaleCommand,
    CreateSaleCommand,
    SalesApplicationService,
)
from evopharm_retail_erp.application.common import UnitOfWork
from evopharm_retail_erp.domain.sales import SaleId
from ..dependencies import get_sale_service, get_uow
from ..schemas.sales import (
    AddSaleLineRequest,
    CreateSaleRequest,
    SaleLineResponse,
    SaleResponse,
)

router = APIRouter(prefix="/api/v1/sales", tags=["Sales / Point of Sale"])


@router.post("", response_model=SaleResponse, status_code=201, summary="Create Sale Transaction")
async def create_sale(
    request: CreateSaleRequest,
    service: SalesApplicationService = Depends(get_sale_service),
) -> SaleResponse:
    """Initialize a new retail sale transaction."""
    cmd = CreateSaleCommand(
        customer_id=request.customer_id,
        prescription_number=request.prescription_reference,
    )
    result = await service.create_sale(cmd)
    res = result.value
    return _build_sale_response(res)


@router.post("/{sale_id}/lines", response_model=SaleResponse, summary="Add Sale Line Item")
async def add_sale_line(
    sale_id: UUID,
    request: AddSaleLineRequest,
    service: SalesApplicationService = Depends(get_sale_service),
) -> SaleResponse:
    """Add a dispensing line item to an active sale transaction."""
    cmd = AddSaleLineCommand(
        sale_id=sale_id,
        medicine_id=request.medicine_id,
        quantity=request.quantity,
        unit_price=request.unit_price,
        batch_id=request.medicine_batch_id,
        discount_percentage=request.discount_percentage,
        tax_rate_percentage=request.tax_rate_percentage,
    )
    result = await service.add_line(cmd)
    res = result.value
    return _build_sale_response(res)


@router.post("/{sale_id}/complete", response_model=SaleResponse, summary="Complete Sale Transaction")
async def complete_sale(
    sale_id: UUID,
    service: SalesApplicationService = Depends(get_sale_service),
) -> SaleResponse:
    """Complete and finalize a retail sale transaction."""
    cmd = CompleteSaleCommand(sale_id=sale_id)
    result = await service.complete_sale(cmd)
    res = result.value
    return _build_sale_response(res)


@router.get("/{sale_id}", response_model=SaleResponse, summary="Get Sale by ID")
async def get_sale_by_id(
    sale_id: UUID,
    uow: UnitOfWork = Depends(get_uow),
) -> SaleResponse:
    """Retrieve sale details by ID."""
    async with uow as active_uow:
        sale = active_uow.sales.get_by_id(SaleId(sale_id))
        if sale is None:
            raise HTTPException(status_code=404, detail=f"Sale {sale_id} not found")

        from evopharm_retail_erp.application.sales.results import SaleResult
        res = SaleResult.from_domain(sale)
        return _build_sale_response(res)


def _build_sale_response(res) -> SaleResponse:
    cust_id: UUID | None = None
    if res.customer and res.customer.customer_id:
        cust_id = res.customer.customer_id

    lines = []
    for line in res.lines:
        u_price = line.unit_price.amount if hasattr(line.unit_price, "amount") else line.unit_price
        lines.append(
            SaleLineResponse(
                id=line.line_id,
                medicine_id=line.medicine_id,
                medicine_batch_id=line.batch_id if line.batch_id else line.medicine_id,
                quantity=line.quantity,
                unit_price=u_price,
                line_total=line.line_total,
            )
        )

    return SaleResponse(
        id=res.sale_id,
        receipt_number=res.invoice_number,
        customer_id=cust_id,
        status=res.sale_status,
        total_amount=res.total.net_total,
        lines=lines,
        version=res.version,
    )
