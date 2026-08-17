"""Unit tests for CustomerApplicationService orchestration."""
from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
from types import TracebackType
from unittest import IsolatedAsyncioTestCase
from uuid import uuid4

from evopharm_retail_erp.application.common import UnitOfWork
from evopharm_retail_erp.application.customer import (
    ActivateCustomerCommand,
    CustomerApplicationService,
    CustomerNotFoundError,
    DeactivateCustomerCommand,
    RegisterCustomerCommand,
    SuspendCustomerCommand,
    UpdateCustomerAddressCommand,
    UpdateCustomerContactCommand,
    UpdateCustomerProfileCommand,
)
from evopharm_retail_erp.domain.customer import (
    Customer,
    CustomerAlreadyActiveError,
    CustomerAlreadyInactiveError,
    CustomerCode,
    CustomerId,
    CustomerRepository,
    CustomerStatus,
    PhoneNumber,
)


class InMemoryCustomerRepository(CustomerRepository):
    def __init__(self) -> None:
        self.store: dict[CustomerId, Customer] = {}

    def add(self, customer: Customer) -> None:
        if customer.id in self.store:
            raise ValueError("Duplicate customer ID")
        self.store[customer.id] = deepcopy(customer)

    def save(self, customer: Customer) -> None:
        if customer.id not in self.store:
            raise KeyError("Customer not found")
        self.store[customer.id] = deepcopy(customer)

    def get_by_id(self, customer_id: CustomerId) -> Customer | None:
        item = self.store.get(customer_id)
        return deepcopy(item) if item else None

    def get_by_code(self, code: CustomerCode) -> Customer | None:
        for item in self.store.values():
            if item.code == code:
                return deepcopy(item)
        return None

    def get_by_phone(self, phone: PhoneNumber) -> Customer | None:
        for item in self.store.values():
            if item.phone == phone:
                return deepcopy(item)
        return None

    def list_by_status(
        self, status: CustomerStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Customer]:
        return [deepcopy(item) for item in self.store.values() if item.status == status]

    def count_by_status(self, status: CustomerStatus) -> int:
        return sum(1 for item in self.store.values() if item.status == status)

    def exists(self, customer_id: CustomerId) -> bool:
        return customer_id in self.store

    def exists_code(self, code: CustomerCode) -> bool:
        return any(item.code == code for item in self.store.values())


class FakeUnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        self.customer = InMemoryCustomerRepository()
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


class CustomerApplicationServiceTests(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.uow = FakeUnitOfWork()
        self.service = CustomerApplicationService(self.uow)

    async def test_register_customer_use_case(self) -> None:
        cmd = RegisterCustomerCommand(
            name="Charlie Brown",
            phone="9876543210",
            email="charlie@peanuts.com",
            street="10 Wall Street",
            city="Mumbai",
            state="Maharashtra",
            pincode="400001",
        )
        res = await self.service.register_customer(cmd)

        self.assertTrue(res.is_success)
        self.assertTrue(self.uow.committed)
        self.assertEqual(res.value.name, "Charlie Brown")
        self.assertEqual(res.value.status, "ACTIVE")

    async def test_update_contact_address_profile_use_cases(self) -> None:
        reg_res = await self.service.register_customer(
            RegisterCustomerCommand(name="Diana Prince", phone="9876543210")
        )
        c_id = reg_res.value.customer_id

        # Update contact
        c_res = await self.service.update_contact_information(
            UpdateCustomerContactCommand(customer_id=c_id, phone="9111122223", email="diana@amazon.com")
        )
        self.assertEqual(c_res.value.phone, "9111122223")
        self.assertEqual(c_res.value.email, "diana@amazon.com")

        # Update address
        a_res = await self.service.update_address(
            UpdateCustomerAddressCommand(
                customer_id=c_id, street="20 Park St", city="Kolkata", state="West Bengal", pincode="700016"
            )
        )
        self.assertEqual(a_res.value.address.city, "Kolkata")

        # Update profile
        p_res = await self.service.update_profile(
            UpdateCustomerProfileCommand(customer_id=c_id, name="Diana Prince Wonder", customer_type="VIP")
        )
        self.assertEqual(p_res.value.name, "Diana Prince Wonder")
        self.assertEqual(p_res.value.customer_type, "VIP")

    async def test_lifecycle_deactivate_activate_suspend(self) -> None:
        reg_res = await self.service.register_customer(
            RegisterCustomerCommand(name="Evan Wright", phone="9876543210")
        )
        c_id = reg_res.value.customer_id

        # Already active error
        with self.assertRaises(CustomerAlreadyActiveError):
            await self.service.activate_customer(ActivateCustomerCommand(customer_id=c_id))

        # Deactivate
        deact_res = await self.service.deactivate_customer(
            DeactivateCustomerCommand(customer_id=c_id, reason="Account closed on request")
        )
        self.assertEqual(deact_res.value.status, "INACTIVE")

        # Reactivate
        act_res = await self.service.activate_customer(
            ActivateCustomerCommand(customer_id=c_id, reason="Reactivated profile")
        )
        self.assertEqual(act_res.value.status, "ACTIVE")

        # Suspend
        susp_res = await self.service.suspend_customer(
            SuspendCustomerCommand(customer_id=c_id, reason="Payment default hold")
        )
        self.assertEqual(susp_res.value.status, "SUSPENDED")

    async def test_get_customer_use_case(self) -> None:
        reg_res = await self.service.register_customer(
            RegisterCustomerCommand(name="Fiona Gallagher", phone="9876543210")
        )
        c_id = reg_res.value.customer_id

        get_res = await self.service.get_customer(c_id)
        self.assertTrue(get_res.is_success)
        self.assertEqual(get_res.value.name, "Fiona Gallagher")

    async def test_customer_not_found_raises_exception(self) -> None:
        missing_id = uuid4()
        with self.assertRaises(CustomerNotFoundError):
            await self.service.get_customer(missing_id)
