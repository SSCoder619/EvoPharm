"""Application-level integration handlers orchestrating cross-context workflows.

Event handlers translate integration event messages into target Application Service commands
while preserving bounded-context decoupling and enforcing in-process idempotency.
"""
from __future__ import annotations

from typing import Protocol, TYPE_CHECKING
from uuid import UUID, uuid4

from ..inventory import InventoryApplicationService, ReceiveStockCommand
from ..invoice import CreateInvoiceCommand, InvoiceApplicationService
from .events import (
    InvoicePaidPayload,
    IntegrationEvent,
    PurchaseReceivedPayload,
    SaleCompletedPayload,
    SaleReturnedPayload,
)
from .exceptions import DuplicateEventError

if TYPE_CHECKING:
    from ..common.result import ApplicationResult
    from ..inventory.results import InventoryResult
    from ..invoice.results import InvoiceResult


class EventTracker(Protocol):
    """Protocol contract for tracking processed integration event IDs (idempotency guard)."""

    def is_processed(self, event_id: UUID) -> bool:
        """Check if an event ID has already been handled."""
        ...

    def mark_processed(self, event_id: UUID) -> None:
        """Mark an event ID as successfully processed."""
        ...


class InMemoryEventTracker:
    """In-memory implementation of the EventTracker protocol for testing and local runtime."""

    def __init__(self) -> None:
        self._processed_events: set[UUID] = set()

    def is_processed(self, event_id: UUID) -> bool:
        return event_id in self._processed_events

    def mark_processed(self, event_id: UUID) -> None:
        self._processed_events.add(event_id)


class PurchaseReceivedHandler:
    """Handles purchase stock receipt events by invoking InventoryApplicationService."""

    def __init__(
        self,
        inventory_service: InventoryApplicationService,
        tracker: EventTracker | None = None,
    ) -> None:
        self.inventory_service = inventory_service
        self.tracker = tracker or InMemoryEventTracker()

    async def handle(
        self, event: IntegrationEvent[PurchaseReceivedPayload]
    ) -> ApplicationResult[InventoryResult]:
        """Maps purchase receipt event into inventory stock receipt command."""
        if self.tracker.is_processed(event.event_id):
            raise DuplicateEventError(event.event_id)

        payload = event.payload
        batch_id = payload.batch_id if payload.batch_id else uuid4()

        cmd = ReceiveStockCommand(
            medicine_id=payload.medicine_id,
            medicine_batch_id=batch_id,
            quantity=payload.received_quantity,
            document_type="PURCHASE",
            document_id=payload.purchase_id,
            reference_number=f"PO-{str(payload.purchase_id)[:8]}",
            reason=f"Stock receipt for PO line {str(payload.line_id)[:8]}",
        )

        res = await self.inventory_service.receive_stock(cmd)
        if res.is_success:
            self.tracker.mark_processed(event.event_id)
        return res


class SaleCompletedHandler:
    """Handles completed sale events by triggering Invoice creation."""

    def __init__(
        self,
        invoice_service: InvoiceApplicationService,
        tracker: EventTracker | None = None,
    ) -> None:
        self.invoice_service = invoice_service
        self.tracker = tracker or InMemoryEventTracker()

    async def handle(
        self, event: IntegrationEvent[SaleCompletedPayload]
    ) -> ApplicationResult[InvoiceResult]:
        """Maps completed sale event into invoice creation command."""
        if self.tracker.is_processed(event.event_id):
            raise DuplicateEventError(event.event_id)

        payload = event.payload
        cmd = CreateInvoiceCommand(
            sale_id=payload.sale_id,
            sale_invoice_number=payload.invoice_number,
            customer_id=payload.customer_id,
            customer_name=payload.customer_name,
        )

        res = await self.invoice_service.create_invoice(cmd)
        if res.is_success:
            self.tracker.mark_processed(event.event_id)
        return res


class SaleReturnedHandler:
    """Handles returned sale events by restoring Inventory stock."""

    def __init__(
        self,
        inventory_service: InventoryApplicationService,
        tracker: EventTracker | None = None,
    ) -> None:
        self.inventory_service = inventory_service
        self.tracker = tracker or InMemoryEventTracker()

    async def handle(
        self, event: IntegrationEvent[SaleReturnedPayload]
    ) -> ApplicationResult[InventoryResult]:
        """Maps sale return event into inventory stock restoration command."""
        if self.tracker.is_processed(event.event_id):
            raise DuplicateEventError(event.event_id)

        payload = event.payload
        batch_id = payload.batch_id if payload.batch_id else uuid4()

        cmd = ReceiveStockCommand(
            medicine_id=payload.medicine_id,
            medicine_batch_id=batch_id,
            quantity=payload.returned_quantity,
            document_type="SALE_RETURN",
            document_id=payload.sale_id,
            reference_number=f"SR-{str(payload.sale_id)[:8]}",
            reason=f"Stock return: {payload.return_reason}",
        )

        res = await self.inventory_service.receive_stock(cmd)
        if res.is_success:
            self.tracker.mark_processed(event.event_id)
        return res


class InvoicePaidHandler:
    """Handles fully paid invoice events exposing accounting/payment integration boundary."""

    def __init__(self, tracker: EventTracker | None = None) -> None:
        self.tracker = tracker or InMemoryEventTracker()
        self.processed_log: list[UUID] = []

    async def handle(
        self, event: IntegrationEvent[InvoicePaidPayload]
    ) -> bool:
        """Processes invoice paid integration event boundary."""
        if self.tracker.is_processed(event.event_id):
            raise DuplicateEventError(event.event_id)

        self.processed_log.append(event.payload.invoice_id)
        self.tracker.mark_processed(event.event_id)
        return True
