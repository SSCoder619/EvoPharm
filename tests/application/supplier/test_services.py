"""Unit tests for SupplierApplicationService orchestration."""
from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
from types import TracebackType
from unittest import IsolatedAsyncioTestCase
from uuid import uuid4

from evopharm_retail_erp.application.common import UnitOfWork
from evopharm_retail_erp.application.supplier import (
    ActivateSupplierCommand,
    DeactivateSupplierCommand,
    ReactivateSupplierCommand,
    RegisterSupplierCommand,
    SupplierApplicationService,
    SupplierNotFoundError,
    SuspendSupplierCommand,
    UpdateSupplierAddressCommand,
    UpdateSupplierComplianceCommand,
    UpdateSupplierContactCommand,
    UpdateSupplierDetailsCommand,
)
from evopharm_retail_erp.domain.supplier import (
    GSTIN,
    Supplier,
    SupplierAlreadyActiveError,
    SupplierCode,
    SupplierId,
    SupplierRepository,
    SupplierStatus,
)


class InMemorySupplierRepository(SupplierRepository):
    def __init__(self) -> None:
        self.store: dict[SupplierId, Supplier] = {}

    def add(self, supplier: Supplier) -> None:
        if supplier.id in self.store:
            raise ValueError("Duplicate supplier ID")
        self.store[supplier.id] = deepcopy(supplier)

    def save(self, supplier: Supplier) -> None:
        if supplier.id not in self.store:
            raise KeyError("Supplier not found")
        self.store[supplier.id] = deepcopy(supplier)

    def get_by_id(self, supplier_id: SupplierId) -> Supplier | None:
        item = self.store.get(supplier_id)
        return deepcopy(item) if item else None

    def get_by_code(self, code: SupplierCode) -> Supplier | None:
        for item in self.store.values():
            if item.code == code:
                return deepcopy(item)
        return None

    def get_by_gstin(self, gstin: GSTIN) -> Supplier | None:
        for item in self.store.values():
            if item.gstin == gstin:
                return deepcopy(item)
        return None

    def list_by_status(
        self, status: SupplierStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Supplier]:
        return [deepcopy(item) for item in self.store.values() if item.status == status]

    def count_by_status(self, status: SupplierStatus) -> int:
        return sum(1 for item in self.store.values() if item.status == status)

    def exists(self, supplier_id: SupplierId) -> bool:
        return supplier_id in self.store

    def exists_code(self, code: SupplierCode) -> bool:
        return any(item.code == code for item in self.store.values())


class FakeUnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        self.supplier = InMemorySupplierRepository()
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


class SupplierApplicationServiceTests(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.uow = FakeUnitOfWork()
        self.service = SupplierApplicationService(self.uow)

    async def test_register_supplier_use_case(self) -> None:
        cmd = RegisterSupplierCommand(
            name="Lupin Limited",
            phone="9876543210",
            email="contact@lupin.com",
            street="Kalpataru Inspire",
            city="Mumbai",
            state="Maharashtra",
            pincode="400055",
            gstin="27AAACL0011K1Z3",
            pan="AAACL0011K",
            category="MANUFACTURER",
        )
        res = await self.service.register_supplier(cmd)

        self.assertTrue(res.is_success)
        self.assertTrue(self.uow.committed)
        self.assertEqual(res.value.name, "Lupin Limited")
        self.assertTrue(res.value.is_tax_compliant)
        self.assertEqual(res.value.status, "ACTIVE")

    async def test_update_contact_address_compliance_details(self) -> None:
        reg_res = await self.service.register_supplier(
            RegisterSupplierCommand(name="Mankind Pharma", phone="9876543210")
        )
        s_id = reg_res.value.supplier_id

        # Contact update
        c_res = await self.service.update_contact_information(
            UpdateSupplierContactCommand(supplier_id=s_id, phone="9123456789", email="help@mankind.com")
        )
        self.assertEqual(c_res.value.phone, "9123456789")

        # Address update
        a_res = await self.service.update_address(
            UpdateSupplierAddressCommand(
                supplier_id=s_id, street="208 Okhla Phase III", city="New Delhi", state="Delhi", pincode="110020"
            )
        )
        self.assertEqual(a_res.value.address.city, "New Delhi")

        # Compliance update
        comp_res = await self.service.update_compliance_information(
            UpdateSupplierComplianceCommand(supplier_id=s_id, gstin="07AAACM5555P1Z8", pan="AAACM5555P")
        )
        self.assertEqual(comp_res.value.gstin, "07AAACM5555P1Z8")
        self.assertTrue(comp_res.value.is_tax_compliant)

        # Details update
        det_res = await self.service.update_supplier_details(
            UpdateSupplierDetailsCommand(supplier_id=s_id, name="Mankind Specialities", category="WHOLESALER")
        )
        self.assertEqual(det_res.value.name, "Mankind Specialities")
        self.assertEqual(det_res.value.category, "WHOLESALER")

    async def test_lifecycle_deactivate_activate_suspend_reactivate(self) -> None:
        reg_res = await self.service.register_supplier(
            RegisterSupplierCommand(name="Torrent Pharma", phone="9876543210")
        )
        s_id = reg_res.value.supplier_id

        # Already active error
        with self.assertRaises(SupplierAlreadyActiveError):
            await self.service.activate_supplier(ActivateSupplierCommand(supplier_id=s_id))

        # Deactivate
        deact_res = await self.service.deactivate_supplier(
            DeactivateSupplierCommand(supplier_id=s_id, reason="Contract expired")
        )
        self.assertEqual(deact_res.value.status, "INACTIVE")

        # Activate
        act_res = await self.service.activate_supplier(
            ActivateSupplierCommand(supplier_id=s_id, reason="Renewed contract")
        )
        self.assertEqual(act_res.value.status, "ACTIVE")

        # Suspend
        susp_res = await self.service.suspend_supplier(
            SuspendSupplierCommand(supplier_id=s_id, reason="Quality audit hold")
        )
        self.assertEqual(susp_res.value.status, "SUSPENDED")

        # Reactivate
        react_res = await self.service.reactivate_supplier(
            ReactivateSupplierCommand(supplier_id=s_id, reason="Passed audit re-inspection")
        )
        self.assertEqual(react_res.value.status, "ACTIVE")

    async def test_get_supplier_use_case(self) -> None:
        reg_res = await self.service.register_supplier(
            RegisterSupplierCommand(name="Zydus Cadila", phone="9876543210")
        )
        s_id = reg_res.value.supplier_id

        get_res = await self.service.get_supplier(s_id)
        self.assertTrue(get_res.is_success)
        self.assertEqual(get_res.value.name, "Zydus Cadila")

    async def test_supplier_not_found_raises_exception(self) -> None:
        missing_id = uuid4()
        with self.assertRaises(SupplierNotFoundError):
            await self.service.get_supplier(missing_id)
