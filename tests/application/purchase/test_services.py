"""Unit tests for PurchaseApplicationService orchestration."""
from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
from decimal import Decimal
from types import TracebackType
from unittest import IsolatedAsyncioTestCase
from uuid import uuid4

from evopharm_retail_erp.application.common import UnitOfWork
from evopharm_retail_erp.application.purchase import (
    AddPurchaseLineCommand,
    ApprovePurchaseCommand,
    AttachPurchaseInvoiceCommand,
    CancelPurchaseCommand,
    CreatePurchaseCommand,
    PlacePurchaseOrderCommand,
    PurchaseApplicationService,
    PurchaseNotFoundError,
    ReceivePurchaseStockCommand,
    RecordPurchasePaymentCommand,
    RemovePurchaseLineCommand,
)
from evopharm_retail_erp.domain.medicine import MedicineId
from evopharm_retail_erp.domain.purchase import (
    DuplicatePurchaseLineError,
    InvalidPurchaseStateTransitionError,
    InvoiceReference,
    Purchase,
    PurchaseId,
    PurchaseOrderReference,
    PurchaseRepository,
    PurchaseStatus,
    ReceivingStatus,
    SupplierReference,
)


class InMemoryPurchaseRepository(PurchaseRepository):
    def __init__(self) -> None:
        self.store: dict[PurchaseId, Purchase] = {}

    def add(self, purchase: Purchase) -> None:
        if purchase.id in self.store:
            raise ValueError("Duplicate purchase ID")
        self.store[purchase.id] = deepcopy(purchase)

    def save(self, purchase: Purchase) -> None:
        if purchase.id not in self.store:
            raise KeyError("Purchase not found")
        self.store[purchase.id] = deepcopy(purchase)

    def get_by_id(self, purchase_id: PurchaseId) -> Purchase | None:
        item = self.store.get(purchase_id)
        return deepcopy(item) if item else None

    def get_by_order_reference(
        self, order_reference: PurchaseOrderReference
    ) -> Purchase | None:
        for p in self.store.values():
            if p.order_reference == order_reference:
                return deepcopy(p)
        return None

    def get_by_invoice_reference(
        self, invoice_reference: InvoiceReference
    ) -> Purchase | None:
        for p in self.store.values():
            if p.invoice_reference == invoice_reference:
                return deepcopy(p)
        return None

    def list_by_supplier(
        self, supplier_id: SupplierReference | str | UUID, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Purchase]:
        target_str = str(supplier_id.supplier_id) if isinstance(supplier_id, SupplierReference) else str(supplier_id)
        return [deepcopy(p) for p in self.store.values() if str(p.supplier_reference.supplier_id) == target_str]

    def list_by_status(
        self, status: PurchaseStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Purchase]:
        return [deepcopy(p) for p in self.store.values() if p.purchase_status == status]

    def list_by_receiving_status(
        self, receiving_status: ReceivingStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Purchase]:
        return [deepcopy(p) for p in self.store.values() if p.receiving_status == receiving_status]

    def count_by_status(self, status: PurchaseStatus) -> int:
        return sum(1 for p in self.store.values() if p.purchase_status == status)

    def exists(self, purchase_id: PurchaseId) -> bool:
        return purchase_id in self.store

    def exists_order_reference(self, order_reference: PurchaseOrderReference) -> bool:
        return any(p.order_reference == order_reference for p in self.store.values())


class FakeUnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        self.purchases = InMemoryPurchaseRepository()
        self.committed: bool = False
        self.rolled_back: bool = False

    async def __aenter__(self) -> FakeUnitOfWork:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


class PurchaseApplicationServiceTests(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.uow = FakeUnitOfWork()
        self.service = PurchaseApplicationService(self.uow)
        self.sup_id = uuid4()
        self.med_id = uuid4()

    async def test_create_purchase_use_case(self) -> None:
        cmd = CreatePurchaseCommand(supplier_id=self.sup_id, order_reference="PO-2026-01")
        res = await self.service.create_purchase(cmd)

        self.assertTrue(res.is_success)
        self.assertTrue(self.uow.committed)
        self.assertEqual(res.value.supplier_id, self.sup_id)
        self.assertEqual(res.value.order_reference, "PO-2026-01")
        self.assertEqual(res.value.purchase_status, "DRAFT")

    async def test_add_and_remove_line_use_case(self) -> None:
        create_res = await self.service.create_purchase(
            CreatePurchaseCommand(supplier_id=self.sup_id)
        )
        p_id = create_res.value.purchase_id

        add_cmd = AddPurchaseLineCommand(
            purchase_id=p_id,
            medicine_id=self.med_id,
            ordered_quantity=10,
            unit_price=Decimal("50.00"),
            discount_percentage=Decimal("10.00"),
            tax_rate_percentage=Decimal("18.00"),
        )
        add_res = await self.service.add_line(add_cmd)

        self.assertTrue(add_res.is_success)
        self.assertEqual(len(add_res.value.lines), 1)

        line_id = add_res.value.lines[0].line_id

        # Duplicate line rejection
        with self.assertRaises(DuplicatePurchaseLineError):
            await self.service.add_line(add_cmd)

        rem_res = await self.service.remove_line(
            RemovePurchaseLineCommand(purchase_id=p_id, line_id=line_id)
        )
        self.assertTrue(rem_res.is_success)
        self.assertEqual(len(rem_res.value.lines), 0)

    async def test_full_purchase_lifecycle_approve_order_receive(self) -> None:
        c_res = await self.service.create_purchase(
            CreatePurchaseCommand(supplier_id=self.sup_id)
        )
        p_id = c_res.value.purchase_id

        await self.service.add_line(
            AddPurchaseLineCommand(
                purchase_id=p_id,
                medicine_id=self.med_id,
                ordered_quantity=5,
                unit_price=Decimal("100.00"),
            )
        )

        # 1. Approve
        app_res = await self.service.approve_purchase(
            ApprovePurchaseCommand(purchase_id=p_id)
        )
        self.assertEqual(app_res.value.purchase_status, "APPROVED")

        # 2. Place Order
        ord_res = await self.service.place_order(
            PlacePurchaseOrderCommand(purchase_id=p_id)
        )
        self.assertEqual(ord_res.value.purchase_status, "ORDERED")

        line_id = ord_res.value.lines[0].line_id

        # 3. Receive Partial Stock
        rec_res1 = await self.service.receive_stock(
            ReceivePurchaseStockCommand(
                purchase_id=p_id,
                line_id=line_id,
                quantity=3,
                batch_number="BATCH-001",
            )
        )
        self.assertEqual(rec_res1.value.purchase_status, "PARTIALLY_RECEIVED")
        self.assertEqual(rec_res1.value.receiving_status, "PARTIAL")

        # 4. Receive Remaining Stock
        rec_res2 = await self.service.receive_stock(
            ReceivePurchaseStockCommand(
                purchase_id=p_id,
                line_id=line_id,
                quantity=2,
                batch_number="BATCH-001",
            )
        )
        self.assertEqual(rec_res2.value.purchase_status, "RECEIVED")
        self.assertEqual(rec_res2.value.receiving_status, "COMPLETED")

    async def test_cancel_purchase_use_case(self) -> None:
        c_res = await self.service.create_purchase(
            CreatePurchaseCommand(supplier_id=self.sup_id)
        )
        p_id = c_res.value.purchase_id

        cancel_res = await self.service.cancel_purchase(
            CancelPurchaseCommand(purchase_id=p_id, reason="Supplier out of stock")
        )
        self.assertEqual(cancel_res.value.purchase_status, "CANCELLED")

    async def test_attach_invoice_and_record_payment(self) -> None:
        c_res = await self.service.create_purchase(
            CreatePurchaseCommand(supplier_id=self.sup_id)
        )
        p_id = c_res.value.purchase_id
        await self.service.add_line(
            AddPurchaseLineCommand(
                purchase_id=p_id,
                medicine_id=self.med_id,
                ordered_quantity=10,
                unit_price=Decimal("10.00"),
            )
        )

        inv_res = await self.service.attach_invoice(
            AttachPurchaseInvoiceCommand(purchase_id=p_id, invoice_number="INV-SUP-99")
        )
        self.assertEqual(inv_res.value.invoice_reference, "INV-SUP-99")

        pay_res = await self.service.record_payment(
            RecordPurchasePaymentCommand(purchase_id=p_id, amount_paid=Decimal("100.00"))
        )
        self.assertEqual(pay_res.value.payment_status, "PAID")

    async def test_purchase_not_found_raises_exception(self) -> None:
        missing_id = uuid4()
        with self.assertRaises(PurchaseNotFoundError):
            await self.service.approve_purchase(
                ApprovePurchaseCommand(purchase_id=missing_id)
            )
