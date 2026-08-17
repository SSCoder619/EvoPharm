"""Invoice & Billing API router."""
from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException

from evopharm_retail_erp.application.invoice import (
    AddInvoiceLineCommand,
    CreateInvoiceCommand,
    InvoiceApplicationService,
    RecordInvoicePaymentCommand,
)
from evopharm_retail_erp.application.common import UnitOfWork
from evopharm_retail_erp.domain.invoice import InvoiceId
from ..dependencies import get_invoice_service, get_uow
from ..schemas.invoice import (
    CreateInvoiceRequest,
    InvoiceResponse,
    RecordPaymentRequest,
)
from ..schemas.purchase import AddPurchaseLineRequest

router = APIRouter(prefix="/api/v1/invoices", tags=["Invoice & Billing"])


@router.post("", response_model=InvoiceResponse, status_code=201, summary="Generate Invoice")
async def create_invoice(
    request: CreateInvoiceRequest,
    service: InvoiceApplicationService = Depends(get_invoice_service),
) -> InvoiceResponse:
    """Generate a commercial invoice for a sale or purchase order."""
    cmd = CreateInvoiceCommand(
        sale_id=request.source_document_id if request.source_document_type == "SALE" else None,
        customer_id=request.customer_id,
    )
    result = await service.create_invoice(cmd)
    res = result.value
    return InvoiceResponse(
        id=res.invoice_id,
        invoice_number=res.number,
        total_amount=res.total.net_total,
        paid_amount=res.total_amount_paid,
        status=res.status,
        version=res.version,
    )


@router.post("/{invoice_id}/lines", response_model=InvoiceResponse, summary="Add Invoice Line Item")
async def add_invoice_line(
    invoice_id: UUID,
    request: AddPurchaseLineRequest,
    service: InvoiceApplicationService = Depends(get_invoice_service),
) -> InvoiceResponse:
    """Add a line item to a draft commercial invoice."""
    cmd = AddInvoiceLineCommand(
        invoice_id=invoice_id,
        medicine_id=request.medicine_id,
        quantity=request.ordered_quantity,
        unit_price=request.unit_price,
        discount_percentage=request.discount_percentage,
        tax_rate_percentage=request.tax_rate_percentage,
    )
    result = await service.add_line(cmd)
    res = result.value
    return InvoiceResponse(
        id=res.invoice_id,
        invoice_number=res.number,
        total_amount=res.total.net_total,
        paid_amount=res.total_amount_paid,
        status=res.status,
        version=res.version,
    )


@router.get("/{invoice_id}", response_model=InvoiceResponse, summary="Get Invoice by ID")
async def get_invoice_by_id(
    invoice_id: UUID,
    uow: UnitOfWork = Depends(get_uow),
) -> InvoiceResponse:
    """Retrieve invoice details by ID."""
    async with uow as active_uow:
        invoice = active_uow.invoice.get_by_id(InvoiceId(invoice_id))
        if invoice is None:
            raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")

        from evopharm_retail_erp.application.invoice.results import InvoiceResult
        res = InvoiceResult.from_domain(invoice)
        return InvoiceResponse(
            id=res.invoice_id,
            invoice_number=res.number,
            total_amount=res.total.net_total,
            paid_amount=res.total_amount_paid,
            status=res.status,
            version=res.version,
        )


@router.post("/{invoice_id}/payments", response_model=InvoiceResponse, summary="Record Invoice Payment")
async def record_payment(
    invoice_id: UUID,
    request: RecordPaymentRequest,
    service: InvoiceApplicationService = Depends(get_invoice_service),
) -> InvoiceResponse:
    """Record a commercial payment settlement against an invoice."""
    cmd = RecordInvoicePaymentCommand(
        invoice_id=invoice_id,
        amount_paid=request.payment_amount,
    )
    result = await service.record_payment(cmd)
    res = result.value
    return InvoiceResponse(
        id=res.invoice_id,
        invoice_number=res.number,
        total_amount=res.total.net_total,
        paid_amount=res.total_amount_paid,
        status=res.status,
        version=res.version,
    )
