"""Unit tests for Application Integration event handlers."""
from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
from types import TracebackType
from unittest import IsolatedAsyncioTestCase
from uuid import uuid4

from evopharm_retail_erp.application.common import UnitOfWork
from evopharm_retail_erp.application.inventory import (
    InventoryApplicationService,
)
from evopharm_retail_erp.application.invoice import (
    InvoiceApplicationService,
)
from evopharm_retail_erp.application.integration import (
    DuplicateEventError,
    InMemoryEventTracker,
    IntegrationEvent,
    InvoicePaidHandler,
    InvoicePaidPayload,
    PurchaseReceivedHandler,
    PurchaseReceivedPayload,
    SaleCompletedHandler,
    SaleCompletedPayload,
    SaleReturnedHandler,
    SaleReturnedPayload,
)
from evopharm_retail_erp.domain.inventory import (
    Inventory,
    InventoryId,
    InventoryRepository,
    StockStatus,
)
from evopharm_retail_erp.domain.invoice import (
    Invoice,
    InvoiceId,
    InvoiceNumber,
    InvoiceRepository,
    InvoiceStatus,
    SaleReference,
)
from evopharm_retail_erp.domain.medicine import MedicineBatchId, MedicineId


class InMemoryInventoryRepo(InventoryRepository):
    def __init__(self) -> None:
        self.store: dict[InventoryId, Inventory] = {}

    def add(self, inventory: Inventory) -> None:
        self.store[inventory.id] = deepcopy(inventory)

    def save(self, inventory: Inventory) -> None:
        self.store[inventory.id] = deepcopy(inventory)

    def get_by_id(self, inventory_id: InventoryId) -> Inventory | None:
        item = self.store.get(inventory_id)
        return deepcopy(item) if item else None

    def get_by_batch_id(self, batch_id: MedicineBatchId) -> Inventory | None:
        for item in self.store.values():
            if item.medicine_batch_id == batch_id:
                return deepcopy(item)
        return None

    def list_by_medicine_id(self, medicine_id: MedicineId) -> Sequence[Inventory]:
        return [deepcopy(item) for item in self.store.values() if item.medicine_id == medicine_id]

    def list_by_status(self, status: StockStatus, *, offset: int = 0, limit: int = 50) -> Sequence[Inventory]:
        return [deepcopy(item) for item in self.store.values() if item.status == status]

    def list_low_stock(self, *, offset: int = 0, limit: int = 50) -> Sequence[Inventory]:
        return []

    def list_out_of_stock(self, *, offset: int = 0, limit: int = 50) -> Sequence[Inventory]:
        return []

    def list_overstocked(self, *, offset: int = 0, limit: int = 50) -> Sequence[Inventory]:
        return []

    def count_by_status(self, status: StockStatus) -> int:
        return sum(1 for item in self.store.values() if item.status == status)

    def exists(self, inventory_id: InventoryId) -> bool:
        return inventory_id in self.store

    def exists_for_batch(self, batch_id: MedicineBatchId) -> bool:
        return any(item.medicine_batch_id == batch_id for item in self.store.values())


class InMemoryInvoiceRepo(InvoiceRepository):
    def __init__(self) -> None:
        self.store: dict[InvoiceId, Invoice] = {}

    def add(self, invoice: Invoice) -> None:
        self.store[invoice.id] = deepcopy(invoice)

    def save(self, invoice: Invoice) -> None:
        self.store[invoice.id] = deepcopy(invoice)

    def get_by_id(self, invoice_id: InvoiceId) -> Invoice | None:
        item = self.store.get(invoice_id)
        return deepcopy(item) if item else None

    def get_by_number(self, number: InvoiceNumber) -> Invoice | None:
        for item in self.store.values():
            if item.number == number:
                return deepcopy(item)
        return None

    def find_by_sale_reference(self, sale_reference: SaleReference) -> Invoice | None:
        for item in self.store.values():
            if item.sale_reference == sale_reference:
                return deepcopy(item)
        return None

    def list_by_status(self, status: InvoiceStatus, *, offset: int = 0, limit: int = 50) -> Sequence[Invoice]:
        return [deepcopy(item) for item in self.store.values() if item.status == status]

    def count_by_status(self, status: InvoiceStatus) -> int:
        return sum(1 for item in self.store.values() if item.status == status)

    def exists(self, invoice_id: InvoiceId) -> bool:
        return invoice_id in self.store

    def exists_number(self, number: InvoiceNumber) -> bool:
        return any(item.number == number for item in self.store.values())


class FakeUnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        self.inventory = InMemoryInventoryRepo()
        self.invoice = InMemoryInvoiceRepo()

    async def __aenter__(self) -> FakeUnitOfWork:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass


class IntegrationHandlersTests(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.uow = FakeUnitOfWork()
        self.inventory_service = InventoryApplicationService(self.uow)
        self.invoice_service = InvoiceApplicationService(self.uow)
        self.tracker = InMemoryEventTracker()

    async def test_purchase_received_handler(self) -> None:
        handler = PurchaseReceivedHandler(self.inventory_service, self.tracker)
        event = IntegrationEvent.create(
            source_context="purchase",
            event_type="PurchaseReceived",
            payload=PurchaseReceivedPayload(
                purchase_id=uuid4(),
                line_id=uuid4(),
                medicine_id=uuid4(),
                received_quantity=100,
                batch_number="B-100",
            ),
        )

        res = await handler.handle(event)
        self.assertTrue(res.is_success)
        self.assertEqual(res.value.quantity_on_hand, 100)

        # Idempotency check
        with self.assertRaises(DuplicateEventError):
            await handler.handle(event)

    async def test_sale_completed_handler(self) -> None:
        handler = SaleCompletedHandler(self.invoice_service, self.tracker)
        event = IntegrationEvent.create(
            source_context="sales",
            event_type="SaleCompleted",
            payload=SaleCompletedPayload(
                sale_id=uuid4(),
                invoice_number="INV-SALE-888",
                customer_name="Walk-in Customer",
            ),
        )

        res = await handler.handle(event)
        self.assertTrue(res.is_success)
        self.assertEqual(res.value.customer.name, "Walk-in Customer")

        # Idempotency check
        with self.assertRaises(DuplicateEventError):
            await handler.handle(event)

    async def test_sale_returned_handler(self) -> None:
        handler = SaleReturnedHandler(self.inventory_service, self.tracker)
        event = IntegrationEvent.create(
            source_context="sales",
            event_type="SaleReturned",
            payload=SaleReturnedPayload(
                sale_id=uuid4(),
                line_id=uuid4(),
                medicine_id=uuid4(),
                returned_quantity=15,
                return_reason="Damaged blister pack",
            ),
        )

        res = await handler.handle(event)
        self.assertTrue(res.is_success)
        self.assertEqual(res.value.quantity_on_hand, 15)

    async def test_invoice_paid_handler(self) -> None:
        handler = InvoicePaidHandler(self.tracker)
        i_id = uuid4()
        event = IntegrationEvent.create(
            source_context="invoice",
            event_type="InvoicePaid",
            payload=InvoicePaidPayload(
                invoice_id=i_id,
                invoice_number="INV-2026-777",
                total_amount="2500.00",
            ),
        )

        res = await handler.handle(event)
        self.assertTrue(res)
        self.assertEqual(handler.processed_log, [i_id])
