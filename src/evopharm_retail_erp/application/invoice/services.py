"""Application service for orchestrating Invoice use cases.

Translates application commands into Invoice aggregate calls, manages repository persistence,
and commits database transactions via the UnitOfWork port boundary.
"""
from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from ...domain.invoice import (
    CustomerReference,
    DiscountAmount,
    Invoice,
    InvoiceId,
    InvoiceLineId,
    InvoiceNumber,
    InvoiceQuantity,
    InvoiceType,
    Money,
    SaleReference,
    TaxRate,
    TaxType,
    UnitPrice,
)
from ...domain.medicine import MedicineBatchId, MedicineId
from ..common.result import ApplicationResult
from .commands import (
    AddInvoiceLineCommand,
    CancelInvoiceCommand,
    CreateInvoiceCommand,
    IssueInvoiceCommand,
    RecordInvoicePaymentCommand,
    RemoveInvoiceLineCommand,
)
from .exceptions import InvoiceNotFoundError
from .results import InvoiceResult

if TYPE_CHECKING:
    from ..common.unit_of_work import UnitOfWork


class InvoiceApplicationService:
    """Orchestrates commercial billing invoice workflows across repositories and UnitOfWork boundaries."""

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def create_invoice(
        self, command: CreateInvoiceCommand
    ) -> ApplicationResult[InvoiceResult]:
        """Orchestrates creation of a new draft billing invoice."""
        async with self.uow as uow:
            sale_ref = (
                SaleReference(
                    sale_id=command.sale_id,
                    sale_invoice_number=command.sale_invoice_number,
                )
                if command.sale_id is not None
                else None
            )

            cust_ref = (
                CustomerReference(
                    customer_id=UUID(str(command.customer_id)) if isinstance(command.customer_id, str) else command.customer_id,
                    name=command.customer_name,
                    gstin=command.customer_gstin,
                )
                if (command.customer_id or command.customer_name or command.customer_gstin)
                else None
            )

            inv_num = InvoiceNumber(command.invoice_number) if command.invoice_number else None
            inv_type = InvoiceType(command.invoice_type)
            tax_type = TaxType(command.tax_type)
            i_id = InvoiceId(command.invoice_id) if command.invoice_id else None

            invoice = Invoice.create(
                number=inv_num,
                sale_reference=sale_ref,
                customer_reference=cust_ref,
                invoice_type=inv_type,
                tax_type=tax_type,
                id=i_id,
            )

            uow.invoice.add(invoice)
            await uow.commit()
            return ApplicationResult.success(InvoiceResult.from_domain(invoice))

    async def add_line(
        self, command: AddInvoiceLineCommand
    ) -> ApplicationResult[InvoiceResult]:
        """Orchestrates adding an item line to a draft invoice."""
        async with self.uow as uow:
            i_id = InvoiceId(command.invoice_id)
            invoice = uow.invoice.get_by_id(i_id)
            if invoice is None:
                raise InvoiceNotFoundError(command.invoice_id)

            med_id = MedicineId(command.medicine_id)
            batch_id = MedicineBatchId(command.batch_id) if command.batch_id else None
            qty = InvoiceQuantity(command.quantity)
            price = UnitPrice.of(command.unit_price)
            disc = DiscountAmount.percent(command.discount_percentage)
            tax = TaxRate.of(command.tax_rate_percentage)
            line_id = InvoiceLineId(command.line_id) if command.line_id else None

            invoice.add_line(
                medicine_id=med_id,
                quantity=qty,
                unit_price=price,
                batch_id=batch_id,
                discount=disc,
                tax_rate=tax,
                line_id=line_id,
            )

            uow.invoice.save(invoice)
            await uow.commit()
            return ApplicationResult.success(InvoiceResult.from_domain(invoice))

    async def remove_line(
        self, command: RemoveInvoiceLineCommand
    ) -> ApplicationResult[InvoiceResult]:
        """Orchestrates removing a line item from a draft invoice."""
        async with self.uow as uow:
            i_id = InvoiceId(command.invoice_id)
            invoice = uow.invoice.get_by_id(i_id)
            if invoice is None:
                raise InvoiceNotFoundError(command.invoice_id)

            line_id = InvoiceLineId(command.line_id)
            invoice.remove_line(line_id)

            uow.invoice.save(invoice)
            await uow.commit()
            return ApplicationResult.success(InvoiceResult.from_domain(invoice))

    async def issue_invoice(
        self, command: IssueInvoiceCommand
    ) -> ApplicationResult[InvoiceResult]:
        """Orchestrates finalizing and issuing a draft invoice."""
        async with self.uow as uow:
            i_id = InvoiceId(command.invoice_id)
            invoice = uow.invoice.get_by_id(i_id)
            if invoice is None:
                raise InvoiceNotFoundError(command.invoice_id)

            invoice.issue()

            uow.invoice.save(invoice)
            await uow.commit()
            return ApplicationResult.success(InvoiceResult.from_domain(invoice))

    async def record_payment(
        self, command: RecordInvoicePaymentCommand
    ) -> ApplicationResult[InvoiceResult]:
        """Orchestrates customer payment settlement against an invoice."""
        async with self.uow as uow:
            i_id = InvoiceId(command.invoice_id)
            invoice = uow.invoice.get_by_id(i_id)
            if invoice is None:
                raise InvoiceNotFoundError(command.invoice_id)

            amount = Money.of(command.amount_paid)
            invoice.record_payment(amount_paid=amount)

            uow.invoice.save(invoice)
            await uow.commit()
            return ApplicationResult.success(InvoiceResult.from_domain(invoice))

    async def cancel_invoice(
        self, command: CancelInvoiceCommand
    ) -> ApplicationResult[InvoiceResult]:
        """Orchestrates cancellation of an invoice."""
        async with self.uow as uow:
            i_id = InvoiceId(command.invoice_id)
            invoice = uow.invoice.get_by_id(i_id)
            if invoice is None:
                raise InvoiceNotFoundError(command.invoice_id)

            invoice.cancel(reason=command.reason)

            uow.invoice.save(invoice)
            await uow.commit()
            return ApplicationResult.success(InvoiceResult.from_domain(invoice))
