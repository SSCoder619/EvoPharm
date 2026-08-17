"""Unit tests for InvoiceApplicationService orchestration."""
from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
from decimal import Decimal
from types import TracebackType
from unittest import IsolatedAsyncioTestCase
from uuid import uuid4

from evopharm_retail_erp.application.common import UnitOfWork
from evopharm_retail_erp.application.invoice import (
    AddInvoiceLineCommand,
    CancelInvoiceCommand,
    CreateInvoiceCommand,
    InvoiceApplicationService,
    InvoiceNotFoundError,
    IssueInvoiceCommand,
    RecordInvoicePaymentCommand,
    RemoveInvoiceLineCommand,
)
from evopharm_retail_erp.domain.invoice import (
    DuplicateInvoiceLineError,
    Invoice,
    InvoiceId,
    InvoiceNumber,
    InvoiceRepository,
    InvoiceStatus,
    OverpaymentError,
    SaleReference,
)
from evopharm_retail_erp.domain.medicine import MedicineId


class InMemoryInvoiceRepository(InvoiceRepository):
    def __init__(self) -> None:
        self.store: dict[InvoiceId, Invoice] = {}

    def add(self, invoice: Invoice) -> None:
        if invoice.id in self.store:
            raise ValueError("Duplicate invoice ID")
        self.store[invoice.id] = deepcopy(invoice)

    def save(self, invoice: Invoice) -> None:
        if invoice.id not in self.store:
            raise KeyError("Invoice not found")
        self.store[invoice.id] = deepcopy(invoice)

    def get_by_id(self, invoice_id: InvoiceId) -> Invoice | None:
        item = self.store.get(invoice_id)
        return deepcopy(item) if item else None

    def get_by_number(self, number: InvoiceNumber) -> Invoice | None:
        for item in self.store.values():
            if item.number == number:
                return deepcopy(item)
        return None

    def find_by_sale_reference(
        self, sale_reference: SaleReference
    ) -> Invoice | None:
        for item in self.store.values():
            if item.sale_reference == sale_reference:
                return deepcopy(item)
        return None

    def list_by_status(
        self, status: InvoiceStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Invoice]:
        return [deepcopy(item) for item in self.store.values() if item.status == status]

    def count_by_status(self, status: InvoiceStatus) -> int:
        return sum(1 for item in self.store.values() if item.status == status)

    def exists(self, invoice_id: InvoiceId) -> bool:
        return invoice_id in self.store

    def exists_number(self, number: InvoiceNumber) -> bool:
        return any(item.number == number for item in self.store.values())


class FakeUnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        self.invoice = InMemoryInvoiceRepository()
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


class InvoiceApplicationServiceTests(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.uow = FakeUnitOfWork()
        self.service = InvoiceApplicationService(self.uow)
        self.med_id = uuid4()
        self.sale_id = uuid4()

    async def test_create_invoice_use_case(self) -> None:
        cmd = CreateInvoiceCommand(
            sale_id=self.sale_id,
            sale_invoice_number="SALE-999",
            customer_name="Grand Healthcare",
            tax_type="INTRA_STATE",
        )
        res = await self.service.create_invoice(cmd)

        self.assertTrue(res.is_success)
        self.assertTrue(self.uow.committed)
        self.assertEqual(res.value.customer.name, "Grand Healthcare")
        self.assertEqual(res.value.sale_reference.sale_id, self.sale_id)
        self.assertEqual(res.value.status, "DRAFT")

    async def test_add_and_remove_line_use_case(self) -> None:
        c_res = await self.service.create_invoice(CreateInvoiceCommand())
        inv_id = c_res.value.invoice_id

        add_cmd = AddInvoiceLineCommand(
            invoice_id=inv_id,
            medicine_id=self.med_id,
            quantity=10,
            unit_price=Decimal("100.00"),
            tax_rate_percentage=Decimal("12.00"),
        )
        add_res = await self.service.add_line(add_cmd)

        self.assertTrue(add_res.is_success)
        self.assertEqual(len(add_res.value.lines), 1)

        line_id = add_res.value.lines[0].line_id

        # Duplicate line rejection
        with self.assertRaises(DuplicateInvoiceLineError):
            await self.service.add_line(add_cmd)

        rem_res = await self.service.remove_line(
            RemoveInvoiceLineCommand(invoice_id=inv_id, line_id=line_id)
        )
        self.assertTrue(rem_res.is_success)
        self.assertEqual(len(rem_res.value.lines), 0)

    async def test_issue_invoice_use_case(self) -> None:
        c_res = await self.service.create_invoice(CreateInvoiceCommand())
        inv_id = c_res.value.invoice_id

        await self.service.add_line(
            AddInvoiceLineCommand(
                invoice_id=inv_id,
                medicine_id=self.med_id,
                quantity=5,
                unit_price=Decimal("50.00"),
            )
        )

        iss_res = await self.service.issue_invoice(IssueInvoiceCommand(invoice_id=inv_id))
        self.assertEqual(iss_res.value.status, "ISSUED")

    async def test_record_partial_and_full_payment_use_case(self) -> None:
        c_res = await self.service.create_invoice(CreateInvoiceCommand())
        inv_id = c_res.value.invoice_id

        await self.service.add_line(
            AddInvoiceLineCommand(
                invoice_id=inv_id,
                medicine_id=self.med_id,
                quantity=10,
                unit_price=Decimal("100.00"),
            )
        )
        await self.service.issue_invoice(IssueInvoiceCommand(invoice_id=inv_id))

        # Net total = 10 * 100 = 1000
        # 1. Partial payment: Rs 400
        pay1 = await self.service.record_payment(
            RecordInvoicePaymentCommand(invoice_id=inv_id, amount_paid=Decimal("400.00"))
        )
        self.assertEqual(pay1.value.payment_status, "PARTIALLY_PAID")
        self.assertEqual(pay1.value.status, "PARTIALLY_PAID")
        self.assertEqual(pay1.value.total_amount_paid, Decimal("400.00"))

        # 2. Overpayment rejection: Rs 700 (400 + 700 > 1000)
        with self.assertRaises(OverpaymentError):
            await self.service.record_payment(
                RecordInvoicePaymentCommand(invoice_id=inv_id, amount_paid=Decimal("700.00"))
            )

        # 3. Final payment: Rs 600
        pay2 = await self.service.record_payment(
            RecordInvoicePaymentCommand(invoice_id=inv_id, amount_paid=Decimal("600.00"))
        )
        self.assertEqual(pay2.value.payment_status, "PAID")
        self.assertEqual(pay2.value.status, "PAID")
        self.assertEqual(pay2.value.total_amount_paid, Decimal("1000.00"))

    async def test_cancel_invoice_use_case(self) -> None:
        c_res = await self.service.create_invoice(CreateInvoiceCommand())
        inv_id = c_res.value.invoice_id

        can_res = await self.service.cancel_invoice(
            CancelInvoiceCommand(invoice_id=inv_id, reason="Customer cancelled order")
        )
        self.assertEqual(can_res.value.status, "CANCELLED")

    async def test_invoice_not_found_raises_exception(self) -> None:
        missing_id = uuid4()
        with self.assertRaises(InvoiceNotFoundError):
            await self.service.issue_invoice(IssueInvoiceCommand(invoice_id=missing_id))
