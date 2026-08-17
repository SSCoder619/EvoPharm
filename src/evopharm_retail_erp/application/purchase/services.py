"""Application service for orchestrating Purchase use cases.

Translates application commands into Purchase aggregate calls, manages repository persistence,
and commits database transactions via the UnitOfWork port boundary.
"""
from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from ...domain.medicine import MedicineId
from ...domain.purchase import (
    Discount,
    InvoiceReference,
    Money,
    Purchase,
    PurchaseId,
    PurchaseLineId,
    PurchaseOrderReference,
    PurchaseQuantity,
    SupplierReference,
    TaxRate,
    UnitPrice,
)
from ..common.result import ApplicationResult
from .commands import (
    AddPurchaseLineCommand,
    ApprovePurchaseCommand,
    AttachPurchaseInvoiceCommand,
    CancelPurchaseCommand,
    CreatePurchaseCommand,
    PlacePurchaseOrderCommand,
    ReceivePurchaseStockCommand,
    RecordPurchasePaymentCommand,
    RemovePurchaseLineCommand,
)
from .exceptions import PurchaseNotFoundError
from .results import PurchaseResult

if TYPE_CHECKING:
    from ..common.unit_of_work import UnitOfWork


class PurchaseApplicationService:
    """Orchestrates purchase workflows across repositories and UnitOfWork boundaries."""

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def create_purchase(
        self, command: CreatePurchaseCommand
    ) -> ApplicationResult[PurchaseResult]:
        """Orchestrates creation of a new draft Purchase Order."""
        async with self.uow as uow:
            sup_ref = SupplierReference.of(command.supplier_id)
            if command.order_reference:
                ord_ref = PurchaseOrderReference(command.order_reference)
            else:
                hex_id = command.purchase_id.hex[:8].upper() if command.purchase_id else uuid4().hex[:8].upper()
                ord_ref = PurchaseOrderReference(f"PO-{hex_id}")

            p_id = PurchaseId(command.purchase_id) if command.purchase_id else None

            purchase = Purchase.create(
                supplier_reference=sup_ref,
                order_reference=ord_ref,
                id=p_id,
            )

            uow.purchases.add(purchase)
            await uow.commit()
            return ApplicationResult.success(PurchaseResult.from_domain(purchase))

    async def add_line(
        self, command: AddPurchaseLineCommand
    ) -> ApplicationResult[PurchaseResult]:
        """Orchestrates adding a line item to a draft Purchase Order."""
        async with self.uow as uow:
            p_id = PurchaseId(command.purchase_id)
            purchase = uow.purchases.get_by_id(p_id)
            if purchase is None:
                raise PurchaseNotFoundError(command.purchase_id)

            med_id = MedicineId(command.medicine_id)
            qty = PurchaseQuantity(command.ordered_quantity)
            price = UnitPrice.of(command.unit_price)
            disc = Discount.percent(command.discount_percentage)
            tax = TaxRate.of(command.tax_rate_percentage)
            line_id = PurchaseLineId(command.line_id) if command.line_id else None

            purchase.add_line(
                medicine_id=med_id,
                ordered_quantity=qty,
                unit_price=price,
                discount=disc,
                tax_rate=tax,
                line_id=line_id,
            )

            uow.purchases.save(purchase)
            await uow.commit()
            return ApplicationResult.success(PurchaseResult.from_domain(purchase))

    async def remove_line(
        self, command: RemovePurchaseLineCommand
    ) -> ApplicationResult[PurchaseResult]:
        """Orchestrates removing a line item from a draft Purchase Order."""
        async with self.uow as uow:
            p_id = PurchaseId(command.purchase_id)
            purchase = uow.purchases.get_by_id(p_id)
            if purchase is None:
                raise PurchaseNotFoundError(command.purchase_id)

            line_id = PurchaseLineId(command.line_id)
            purchase.remove_line(line_id)

            uow.purchases.save(purchase)
            await uow.commit()
            return ApplicationResult.success(PurchaseResult.from_domain(purchase))

    async def approve_purchase(
        self, command: ApprovePurchaseCommand
    ) -> ApplicationResult[PurchaseResult]:
        """Orchestrates approval of a draft Purchase Order."""
        async with self.uow as uow:
            p_id = PurchaseId(command.purchase_id)
            purchase = uow.purchases.get_by_id(p_id)
            if purchase is None:
                raise PurchaseNotFoundError(command.purchase_id)

            purchase.approve(approved_by_user_id=command.approved_by_user_id)

            uow.purchases.save(purchase)
            await uow.commit()
            return ApplicationResult.success(PurchaseResult.from_domain(purchase))

    async def place_order(
        self, command: PlacePurchaseOrderCommand
    ) -> ApplicationResult[PurchaseResult]:
        """Orchestrates transmission/placement of an approved Purchase Order."""
        async with self.uow as uow:
            p_id = PurchaseId(command.purchase_id)
            purchase = uow.purchases.get_by_id(p_id)
            if purchase is None:
                raise PurchaseNotFoundError(command.purchase_id)

            purchase.place_order()

            uow.purchases.save(purchase)
            await uow.commit()
            return ApplicationResult.success(PurchaseResult.from_domain(purchase))

    async def receive_stock(
        self, command: ReceivePurchaseStockCommand
    ) -> ApplicationResult[PurchaseResult]:
        """Orchestrates receiving stock units against an ordered Purchase line."""
        async with self.uow as uow:
            p_id = PurchaseId(command.purchase_id)
            purchase = uow.purchases.get_by_id(p_id)
            if purchase is None:
                raise PurchaseNotFoundError(command.purchase_id)

            line_id = PurchaseLineId(command.line_id)
            qty = PurchaseQuantity(command.quantity)
            purchase.receive_stock(
                line_id=line_id,
                quantity=qty,
                batch_number=command.batch_number,
            )

            uow.purchases.save(purchase)
            await uow.commit()
            return ApplicationResult.success(PurchaseResult.from_domain(purchase))

    async def cancel_purchase(
        self, command: CancelPurchaseCommand
    ) -> ApplicationResult[PurchaseResult]:
        """Orchestrates cancellation of a Purchase Order."""
        async with self.uow as uow:
            p_id = PurchaseId(command.purchase_id)
            purchase = uow.purchases.get_by_id(p_id)
            if purchase is None:
                raise PurchaseNotFoundError(command.purchase_id)

            purchase.cancel(reason=command.reason)

            uow.purchases.save(purchase)
            await uow.commit()
            return ApplicationResult.success(PurchaseResult.from_domain(purchase))

    async def attach_invoice(
        self, command: AttachPurchaseInvoiceCommand
    ) -> ApplicationResult[PurchaseResult]:
        """Orchestrates attaching a commercial supplier invoice reference."""
        async with self.uow as uow:
            p_id = PurchaseId(command.purchase_id)
            purchase = uow.purchases.get_by_id(p_id)
            if purchase is None:
                raise PurchaseNotFoundError(command.purchase_id)

            inv_ref = InvoiceReference(command.invoice_number)
            purchase.attach_invoice(inv_ref)

            uow.purchases.save(purchase)
            await uow.commit()
            return ApplicationResult.success(PurchaseResult.from_domain(purchase))

    async def record_payment(
        self, command: RecordPurchasePaymentCommand
    ) -> ApplicationResult[PurchaseResult]:
        """Orchestrates recording a commercial payment settlement."""
        async with self.uow as uow:
            p_id = PurchaseId(command.purchase_id)
            purchase = uow.purchases.get_by_id(p_id)
            if purchase is None:
                raise PurchaseNotFoundError(command.purchase_id)

            amount = Money.of(command.amount_paid)
            purchase.record_payment(amount)

            uow.purchases.save(purchase)
            await uow.commit()
            return ApplicationResult.success(PurchaseResult.from_domain(purchase))
