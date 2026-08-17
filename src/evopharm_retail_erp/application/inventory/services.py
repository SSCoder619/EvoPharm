"""Application service for orchestrating Inventory use cases.

Translates application commands into Inventory aggregate calls, manages repository persistence,
and commits database transactions via the UnitOfWork port boundary.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from ...domain.inventory import (
    Inventory,
    InventoryId,
    MovementQuantity,
    MovementReason,
    SourceDocumentRef,
    SourceDocumentType,
)
from ...domain.medicine import MedicineBatchId, MedicineId
from ..common.result import ApplicationResult
from .commands import (
    AdjustStockCommand,
    DispenseStockCommand,
    ReceiveStockCommand,
    ReleaseStockCommand,
    ReserveStockCommand,
    TransferStockCommand,
    WriteOffStockCommand,
)
from .exceptions import InventoryNotFoundError
from .results import InventoryResult

if TYPE_CHECKING:
    from ..common.unit_of_work import UnitOfWork


class InventoryApplicationService:
    """Orchestrates inventory stock workflows across repositories and UnitOfWork boundaries."""

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def receive_stock(
        self, command: ReceiveStockCommand
    ) -> ApplicationResult[InventoryResult]:
        """Orchestrates receiving stock units into inventory."""
        async with self.uow as uow:
            inventory: Inventory | None = None
            if command.inventory_id:
                inventory = uow.inventory.get_by_id(InventoryId(command.inventory_id))

            if inventory is None:
                batch_id = MedicineBatchId(command.medicine_batch_id)
                inventory = uow.inventory.get_by_batch_id(batch_id)

            if inventory is None:
                inv_id = InventoryId(command.inventory_id) if command.inventory_id else None
                inventory = Inventory.create(
                    medicine_id=MedicineId(command.medicine_id),
                    medicine_batch_id=MedicineBatchId(command.medicine_batch_id),
                    id=inv_id,
                )
                uow.inventory.add(inventory)

            source_doc = (
                SourceDocumentRef(
                    document_type=SourceDocumentType(command.document_type),
                    document_id=command.document_id,
                    reference_number=command.reference_number,
                )
                if command.document_type and command.document_id and command.reference_number
                else None
            )
            reason = MovementReason(command.reason) if command.reason else None

            inventory.record_receipt(
                quantity=MovementQuantity(command.quantity),
                source_document=source_doc,
                reason=reason,
                performed_by_user_id=command.performed_by_user_id,
            )

            uow.inventory.save(inventory)
            await uow.commit()
            return ApplicationResult.success(InventoryResult.from_domain(inventory))

    async def reserve_stock(
        self, command: ReserveStockCommand
    ) -> ApplicationResult[InventoryResult]:
        """Orchestrates holding stock in reserved state."""
        async with self.uow as uow:
            inv_id = InventoryId(command.inventory_id)
            inventory = uow.inventory.get_by_id(inv_id)
            if inventory is None:
                raise InventoryNotFoundError(command.inventory_id)

            inventory.reserve_stock(MovementQuantity(command.quantity))

            uow.inventory.save(inventory)
            await uow.commit()
            return ApplicationResult.success(InventoryResult.from_domain(inventory))

    async def release_stock(
        self, command: ReleaseStockCommand
    ) -> ApplicationResult[InventoryResult]:
        """Orchestrates releasing reserved stock back to available pool."""
        async with self.uow as uow:
            inv_id = InventoryId(command.inventory_id)
            inventory = uow.inventory.get_by_id(inv_id)
            if inventory is None:
                raise InventoryNotFoundError(command.inventory_id)

            inventory.release_reservation(MovementQuantity(command.quantity))

            uow.inventory.save(inventory)
            await uow.commit()
            return ApplicationResult.success(InventoryResult.from_domain(inventory))

    async def dispense_stock(
        self, command: DispenseStockCommand
    ) -> ApplicationResult[InventoryResult]:
        """Orchestrates dispensing stock units for a retail sale."""
        async with self.uow as uow:
            inv_id = InventoryId(command.inventory_id)
            inventory = uow.inventory.get_by_id(inv_id)
            if inventory is None:
                raise InventoryNotFoundError(command.inventory_id)

            source_doc = (
                SourceDocumentRef(
                    document_type=SourceDocumentType(command.document_type),
                    document_id=command.document_id,
                    reference_number=command.reference_number,
                )
                if command.document_type and command.document_id and command.reference_number
                else None
            )
            reason = MovementReason(command.reason) if command.reason else None

            inventory.record_dispense(
                quantity=MovementQuantity(command.quantity),
                source_document=source_doc,
                reason=reason,
                performed_by_user_id=command.performed_by_user_id,
            )

            uow.inventory.save(inventory)
            await uow.commit()
            return ApplicationResult.success(InventoryResult.from_domain(inventory))

    async def adjust_stock(
        self, command: AdjustStockCommand
    ) -> ApplicationResult[InventoryResult]:
        """Orchestrates manual stock count/damage adjustments."""
        async with self.uow as uow:
            inv_id = InventoryId(command.inventory_id)
            inventory = uow.inventory.get_by_id(inv_id)
            if inventory is None:
                raise InventoryNotFoundError(command.inventory_id)

            source_doc = (
                SourceDocumentRef(
                    document_type=SourceDocumentType(command.document_type),
                    document_id=command.document_id,
                    reference_number=command.reference_number,
                )
                if command.document_type and command.document_id and command.reference_number
                else None
            )
            reason = MovementReason(command.reason)

            inventory.adjust_stock(
                quantity_delta=command.quantity_delta,
                reason=reason,
                source_document=source_doc,
                performed_by_user_id=command.performed_by_user_id,
            )

            uow.inventory.save(inventory)
            await uow.commit()
            return ApplicationResult.success(InventoryResult.from_domain(inventory))

    async def transfer_stock(
        self, command: TransferStockCommand
    ) -> ApplicationResult[tuple[InventoryResult, InventoryResult]]:
        """Orchestrates transferring stock units between two inventory projections."""
        async with self.uow as uow:
            from_id = InventoryId(command.from_inventory_id)
            to_id = InventoryId(command.to_inventory_id)

            from_inv = uow.inventory.get_by_id(from_id)
            if from_inv is None:
                raise InventoryNotFoundError(command.from_inventory_id)

            to_inv = uow.inventory.get_by_id(to_id)
            if to_inv is None:
                raise InventoryNotFoundError(command.to_inventory_id)

            reason = MovementReason(command.reason)
            m_qty = MovementQuantity(command.quantity)

            from_inv.record_dispense(
                quantity=m_qty,
                reason=reason,
                performed_by_user_id=command.performed_by_user_id,
            )
            to_inv.record_receipt(
                quantity=m_qty,
                reason=reason,
                performed_by_user_id=command.performed_by_user_id,
            )

            uow.inventory.save(from_inv)
            uow.inventory.save(to_inv)
            await uow.commit()

            res_from = InventoryResult.from_domain(from_inv)
            res_to = InventoryResult.from_domain(to_inv)
            return ApplicationResult.success((res_from, res_to))

    async def write_off_stock(
        self, command: WriteOffStockCommand
    ) -> ApplicationResult[InventoryResult]:
        """Orchestrates writing off stock due to damage, theft, or expiry."""
        async with self.uow as uow:
            inv_id = InventoryId(command.inventory_id)
            inventory = uow.inventory.get_by_id(inv_id)
            if inventory is None:
                raise InventoryNotFoundError(command.inventory_id)

            reason = MovementReason(command.reason)
            inventory.adjust_stock(
                quantity_delta=-command.quantity,
                reason=reason,
                performed_by_user_id=command.performed_by_user_id,
            )

            uow.inventory.save(inventory)
            await uow.commit()
            return ApplicationResult.success(InventoryResult.from_domain(inventory))
