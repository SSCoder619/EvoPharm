"""Unit tests for SalesApplicationService orchestration."""
from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
from decimal import Decimal
from types import TracebackType
from unittest import IsolatedAsyncioTestCase
from uuid import uuid4

from evopharm_retail_erp.application.common import UnitOfWork
from evopharm_retail_erp.application.sales import (
    AddSaleLineCommand,
    AttachPrescriptionCommand,
    CancelSaleCommand,
    CompleteSaleCommand,
    ConfirmSaleCommand,
    CreateSaleCommand,
    ProcessReturnCommand,
    RecordSalePaymentCommand,
    RemoveSaleLineCommand,
    SaleNotFoundError,
    SalesApplicationService,
)
from evopharm_retail_erp.domain.medicine import MedicineId
from evopharm_retail_erp.domain.sales import (
    CustomerReference,
    DuplicateSaleLineError,
    ExceededSoldQuantityError,
    InvalidSaleStateError,
    InvoiceNumber,
    Sale,
    SaleId,
    SaleRepository,
    SaleStatus,
)


class InMemorySaleRepository(SaleRepository):
    def __init__(self) -> None:
        self.store: dict[SaleId, Sale] = {}

    def add(self, sale: Sale) -> None:
        if sale.id in self.store:
            raise ValueError("Duplicate sale ID")
        self.store[sale.id] = deepcopy(sale)

    def save(self, sale: Sale) -> None:
        if sale.id not in self.store:
            raise KeyError("Sale not found")
        self.store[sale.id] = deepcopy(sale)

    def get_by_id(self, sale_id: SaleId) -> Sale | None:
        item = self.store.get(sale_id)
        return deepcopy(item) if item else None

    def get_by_invoice_number(
        self, invoice_number: InvoiceNumber
    ) -> Sale | None:
        for item in self.store.values():
            if item.invoice_number == invoice_number:
                return deepcopy(item)
        return None

    def list_by_customer(
        self, customer: CustomerReference | str, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Sale]:
        return [deepcopy(item) for item in self.store.values() if str(item.customer_reference) == str(customer)]

    def list_by_status(
        self, status: SaleStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Sale]:
        return [deepcopy(item) for item in self.store.values() if item.sale_status == status]

    def count_by_status(self, status: SaleStatus) -> int:
        return sum(1 for item in self.store.values() if item.sale_status == status)

    def exists(self, sale_id: SaleId) -> bool:
        return sale_id in self.store

    def exists_invoice_number(self, invoice_number: InvoiceNumber) -> bool:
        return any(item.invoice_number == invoice_number for item in self.store.values())


class FakeUnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        self.sales = InMemorySaleRepository()
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


class SalesApplicationServiceTests(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.uow = FakeUnitOfWork()
        self.service = SalesApplicationService(self.uow)
        self.cust_id = uuid4()
        self.med_id = uuid4()

    async def test_create_sale_use_case(self) -> None:
        cmd = CreateSaleCommand(
            customer_id=self.cust_id,
            customer_name="Jane Doe",
            customer_phone="9876543210",
        )
        res = await self.service.create_sale(cmd)

        self.assertTrue(res.is_success)
        self.assertTrue(self.uow.committed)
        self.assertEqual(res.value.customer.customer_id, self.cust_id)
        self.assertEqual(res.value.customer.name, "Jane Doe")
        self.assertEqual(res.value.sale_status, "DRAFT")

    async def test_add_and_remove_line_use_case(self) -> None:
        c_res = await self.service.create_sale(CreateSaleCommand())
        s_id = c_res.value.sale_id

        add_cmd = AddSaleLineCommand(
            sale_id=s_id,
            medicine_id=self.med_id,
            quantity=2,
            unit_price=Decimal("150.00"),
            discount_percentage=Decimal("10.00"),
            tax_rate_percentage=Decimal("18.00"),
        )
        add_res = await self.service.add_line(add_cmd)

        self.assertTrue(add_res.is_success)
        self.assertEqual(len(add_res.value.lines), 1)

        line_id = add_res.value.lines[0].line_id

        # Duplicate line rejection
        with self.assertRaises(DuplicateSaleLineError):
            await self.service.add_line(add_cmd)

        rem_res = await self.service.remove_line(
            RemoveSaleLineCommand(sale_id=s_id, line_id=line_id)
        )
        self.assertTrue(rem_res.is_success)
        self.assertEqual(len(rem_res.value.lines), 0)

    async def test_attach_prescription_use_case(self) -> None:
        c_res = await self.service.create_sale(CreateSaleCommand())
        s_id = c_res.value.sale_id

        rx_cmd = AttachPrescriptionCommand(
            sale_id=s_id,
            prescription_number="RX-777",
            doctor_name="Dr. Gupta",
            doctor_registration_number="REG-9999",
        )
        rx_res = await self.service.attach_prescription(rx_cmd)

        self.assertTrue(rx_res.is_success)
        self.assertIsNotNone(rx_res.value.prescription)
        self.assertEqual(rx_res.value.prescription.prescription_number, "RX-777")

    async def test_full_sale_lifecycle_confirm_pay_complete(self) -> None:
        c_res = await self.service.create_sale(CreateSaleCommand())
        s_id = c_res.value.sale_id

        await self.service.add_line(
            AddSaleLineCommand(
                sale_id=s_id,
                medicine_id=self.med_id,
                quantity=10,
                unit_price=Decimal("10.00"),
            )
        )

        # 1. Confirm
        conf_res = await self.service.confirm_sale(ConfirmSaleCommand(sale_id=s_id))
        self.assertEqual(conf_res.value.sale_status, "CONFIRMED")

        # 2. Record Payment (10 units * Rs 10 = Rs 100)
        pay_res = await self.service.record_payment(
            RecordSalePaymentCommand(
                sale_id=s_id,
                amount_paid=Decimal("100.00"),
                payment_method="UPI",
                payment_reference="UPI-REF-001",
            )
        )
        self.assertEqual(pay_res.value.payment_status, "PAID")
        self.assertEqual(pay_res.value.sale_status, "PAID")

        # 3. Complete
        comp_res = await self.service.complete_sale(CompleteSaleCommand(sale_id=s_id))
        self.assertEqual(comp_res.value.sale_status, "COMPLETED")

    async def test_cancel_sale_use_case(self) -> None:
        c_res = await self.service.create_sale(CreateSaleCommand())
        s_id = c_res.value.sale_id

        cancel_res = await self.service.cancel_sale(
            CancelSaleCommand(sale_id=s_id, reason="Customer walked away")
        )
        self.assertEqual(cancel_res.value.sale_status, "CANCELLED")

    async def test_process_return_use_case(self) -> None:
        c_res = await self.service.create_sale(CreateSaleCommand())
        s_id = c_res.value.sale_id

        add_res = await self.service.add_line(
            AddSaleLineCommand(
                sale_id=s_id,
                medicine_id=self.med_id,
                quantity=4,
                unit_price=Decimal("50.00"),
            )
        )
        line_id = add_res.value.lines[0].line_id

        await self.service.confirm_sale(ConfirmSaleCommand(sale_id=s_id))
        await self.service.record_payment(
            RecordSalePaymentCommand(sale_id=s_id, amount_paid=Decimal("200.00"))
        )
        await self.service.complete_sale(CompleteSaleCommand(sale_id=s_id))

        # Return 2 units
        ret_res = await self.service.process_return(
            ProcessReturnCommand(
                sale_id=s_id,
                line_id=line_id,
                quantity=2,
                reason="CUSTOMER_CHANGED_MIND",
            )
        )

        self.assertTrue(ret_res.is_success)
        self.assertEqual(ret_res.value.refund_amount, Decimal("100.00"))

        # Exceeded return quantity error
        with self.assertRaises(ExceededSoldQuantityError):
            await self.service.process_return(
                ProcessReturnCommand(
                    sale_id=s_id,
                    line_id=line_id,
                    quantity=5,
                )
            )

    async def test_sale_not_found_raises_exception(self) -> None:
        missing_id = uuid4()
        with self.assertRaises(SaleNotFoundError):
            await self.service.confirm_sale(ConfirmSaleCommand(sale_id=missing_id))
