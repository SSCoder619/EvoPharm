"""Application service for orchestrating Sales use cases.

Translates application commands into Sale aggregate calls, manages repository persistence,
and commits database transactions via the UnitOfWork port boundary.
"""
from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from ...domain.medicine import MedicineBatchId, MedicineId
from ...domain.sales import (
    CustomerReference,
    Discount,
    InvoiceNumber,
    Money,
    PaymentMethod,
    PaymentReference,
    PrescriptionReference,
    ReturnReason,
    Sale,
    SaleId,
    SaleLineId,
    SaleQuantity,
    TaxRate,
    UnitPrice,
)
from ..common.result import ApplicationResult
from .commands import (
    AddSaleLineCommand,
    AttachPrescriptionCommand,
    CancelSaleCommand,
    CompleteSaleCommand,
    ConfirmSaleCommand,
    CreateSaleCommand,
    ProcessReturnCommand,
    RecordSalePaymentCommand,
    RemoveSaleLineCommand,
)
from .exceptions import SaleNotFoundError
from .results import SaleResult, SaleReturnResult

if TYPE_CHECKING:
    from ..common.unit_of_work import UnitOfWork


class SalesApplicationService:
    """Orchestrates retail sales dispensing workflows across repositories and UnitOfWork boundaries."""

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def create_sale(
        self, command: CreateSaleCommand
    ) -> ApplicationResult[SaleResult]:
        """Orchestrates creation of a new draft retail sale."""
        async with self.uow as uow:
            cust_ref = CustomerReference.of(
                customer_id=command.customer_id,
                name=command.customer_name,
                phone=command.customer_phone,
            ) if (command.customer_id or command.customer_name or command.customer_phone) else CustomerReference.walk_in()

            inv_num = InvoiceNumber(command.invoice_number) if command.invoice_number else None
            rx_ref = (
                PrescriptionReference(
                    prescription_number=command.prescription_number,
                    doctor_name=command.doctor_name,
                    doctor_registration_number=command.doctor_registration_number,
                )
                if command.prescription_number and command.doctor_name and command.doctor_registration_number
                else None
            )
            s_id = SaleId(command.sale_id) if command.sale_id else None

            sale = Sale.create(
                customer_reference=cust_ref,
                invoice_number=inv_num,
                prescription_reference=rx_ref,
                id=s_id,
            )

            uow.sales.add(sale)
            await uow.commit()
            return ApplicationResult.success(SaleResult.from_domain(sale))

    async def add_line(
        self, command: AddSaleLineCommand
    ) -> ApplicationResult[SaleResult]:
        """Orchestrates adding an item line to a draft retail sale."""
        async with self.uow as uow:
            s_id = SaleId(command.sale_id)
            sale = uow.sales.get_by_id(s_id)
            if sale is None:
                raise SaleNotFoundError(command.sale_id)

            med_id = MedicineId(command.medicine_id)
            batch_id = MedicineBatchId(command.batch_id) if command.batch_id else None
            qty = SaleQuantity(command.quantity)
            price = UnitPrice.of(command.unit_price)
            disc = Discount.percent(command.discount_percentage)
            tax = TaxRate.of(command.tax_rate_percentage)
            line_id = SaleLineId(command.line_id) if command.line_id else None

            sale.add_line(
                medicine_id=med_id,
                quantity=qty,
                unit_price=price,
                batch_id=batch_id,
                discount=disc,
                tax_rate=tax,
                line_id=line_id,
            )

            uow.sales.save(sale)
            await uow.commit()
            return ApplicationResult.success(SaleResult.from_domain(sale))

    async def remove_line(
        self, command: RemoveSaleLineCommand
    ) -> ApplicationResult[SaleResult]:
        """Orchestrates removing a line item from a draft retail sale."""
        async with self.uow as uow:
            s_id = SaleId(command.sale_id)
            sale = uow.sales.get_by_id(s_id)
            if sale is None:
                raise SaleNotFoundError(command.sale_id)

            line_id = SaleLineId(command.line_id)
            sale.remove_line(line_id)

            uow.sales.save(sale)
            await uow.commit()
            return ApplicationResult.success(SaleResult.from_domain(sale))

    async def attach_prescription(
        self, command: AttachPrescriptionCommand
    ) -> ApplicationResult[SaleResult]:
        """Orchestrates attaching prescription details to a retail sale."""
        async with self.uow as uow:
            s_id = SaleId(command.sale_id)
            sale = uow.sales.get_by_id(s_id)
            if sale is None:
                raise SaleNotFoundError(command.sale_id)

            rx_ref = PrescriptionReference(
                prescription_number=command.prescription_number,
                doctor_name=command.doctor_name,
                doctor_registration_number=command.doctor_registration_number,
                prescription_date=command.prescription_date,
            )
            sale.attach_prescription(rx_ref)

            uow.sales.save(sale)
            await uow.commit()
            return ApplicationResult.success(SaleResult.from_domain(sale))

    async def confirm_sale(
        self, command: ConfirmSaleCommand
    ) -> ApplicationResult[SaleResult]:
        """Orchestrates confirmation of a draft retail sale for billing and stock allocation."""
        async with self.uow as uow:
            s_id = SaleId(command.sale_id)
            sale = uow.sales.get_by_id(s_id)
            if sale is None:
                raise SaleNotFoundError(command.sale_id)

            sale.confirm()

            uow.sales.save(sale)
            await uow.commit()
            return ApplicationResult.success(SaleResult.from_domain(sale))

    async def record_payment(
        self, command: RecordSalePaymentCommand
    ) -> ApplicationResult[SaleResult]:
        """Orchestrates customer payment settlement for a sale."""
        async with self.uow as uow:
            s_id = SaleId(command.sale_id)
            sale = uow.sales.get_by_id(s_id)
            if sale is None:
                raise SaleNotFoundError(command.sale_id)

            amount = Money.of(command.amount_paid)
            method = PaymentMethod(command.payment_method)
            pay_ref = PaymentReference(command.payment_reference) if command.payment_reference else None

            sale.record_payment(
                amount_paid=amount,
                payment_method=method,
                payment_reference=pay_ref,
            )

            uow.sales.save(sale)
            await uow.commit()
            return ApplicationResult.success(SaleResult.from_domain(sale))

    async def complete_sale(
        self, command: CompleteSaleCommand
    ) -> ApplicationResult[SaleResult]:
        """Orchestrates completing a paid retail sale."""
        async with self.uow as uow:
            s_id = SaleId(command.sale_id)
            sale = uow.sales.get_by_id(s_id)
            if sale is None:
                raise SaleNotFoundError(command.sale_id)

            sale.complete()

            uow.sales.save(sale)
            await uow.commit()
            return ApplicationResult.success(SaleResult.from_domain(sale))

    async def cancel_sale(
        self, command: CancelSaleCommand
    ) -> ApplicationResult[SaleResult]:
        """Orchestrates cancellation of a retail sale."""
        async with self.uow as uow:
            s_id = SaleId(command.sale_id)
            sale = uow.sales.get_by_id(s_id)
            if sale is None:
                raise SaleNotFoundError(command.sale_id)

            sale.cancel(reason=command.reason)

            uow.sales.save(sale)
            await uow.commit()
            return ApplicationResult.success(SaleResult.from_domain(sale))

    async def process_return(
        self, command: ProcessReturnCommand
    ) -> ApplicationResult[SaleReturnResult]:
        """Orchestrates processing a customer return against a sale line."""
        async with self.uow as uow:
            s_id = SaleId(command.sale_id)
            sale = uow.sales.get_by_id(s_id)
            if sale is None:
                raise SaleNotFoundError(command.sale_id)

            line_id = SaleLineId(command.line_id)
            qty = SaleQuantity(command.quantity)
            reason = ReturnReason(command.reason)

            refund_money = sale.process_return(
                line_id=line_id,
                quantity=qty,
                reason=reason,
            )

            uow.sales.save(sale)
            await uow.commit()

            return ApplicationResult.success(
                SaleReturnResult(
                    refund_amount=refund_money.amount,
                    sale=SaleResult.from_domain(sale),
                )
            )
