"""Contract tests for Customer repository port."""
from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
from unittest import TestCase

from evopharm_retail_erp.domain.customer import (
    Customer,
    CustomerCode,
    CustomerId,
    CustomerName,
    CustomerRepository,
    CustomerStatus,
    PhoneNumber,
)


class InMemoryCustomerRepository(CustomerRepository):
    """In-memory stub implementing CustomerRepository contract for testing."""

    def __init__(self) -> None:
        self._store: dict[CustomerId, Customer] = {}

    def add(self, customer: Customer) -> None:
        if customer.id in self._store:
            raise ValueError("Customer already exists")
        self._store[customer.id] = deepcopy(customer)

    def save(self, customer: Customer) -> None:
        if customer.id not in self._store:
            raise KeyError("Customer not found")
        self._store[customer.id] = deepcopy(customer)

    def get_by_id(self, customer_id: CustomerId) -> Customer | None:
        item = self._store.get(customer_id)
        return deepcopy(item) if item else None

    def get_by_code(self, code: CustomerCode) -> Customer | None:
        for item in self._store.values():
            if item.code == code:
                return deepcopy(item)
        return None

    def get_by_phone(self, phone: PhoneNumber) -> Customer | None:
        for item in self._store.values():
            if item.phone == phone:
                return deepcopy(item)
        return None

    def list_by_status(
        self, status: CustomerStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Customer]:
        return [deepcopy(item) for item in self._store.values() if item.status == status]

    def count_by_status(self, status: CustomerStatus) -> int:
        return sum(1 for item in self._store.values() if item.status == status)

    def exists(self, customer_id: CustomerId) -> bool:
        return customer_id in self._store

    def exists_code(self, code: CustomerCode) -> bool:
        return any(item.code == code for item in self._store.values())


class CustomerRepositoryContractTests(TestCase):
    def setUp(self) -> None:
        self.repository = InMemoryCustomerRepository()
        self.customer = Customer.register(
            name=CustomerName("Charlie Davis"),
            phone=PhoneNumber("+919777766666"),
            code=CustomerCode("CUST-101"),
        )

    def test_add_and_get_by_id(self) -> None:
        self.repository.add(self.customer)
        retrieved = self.repository.get_by_id(self.customer.id)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved, self.customer)
        self.assertTrue(self.repository.exists(self.customer.id))

    def test_get_by_code_and_exists_code(self) -> None:
        self.repository.add(self.customer)
        retrieved = self.repository.get_by_code(self.customer.code)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.code, self.customer.code)
        self.assertTrue(self.repository.exists_code(self.customer.code))

    def test_get_by_phone(self) -> None:
        self.repository.add(self.customer)
        retrieved = self.repository.get_by_phone(self.customer.phone)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.phone, self.customer.phone)

    def test_list_and_count_by_status(self) -> None:
        self.repository.add(self.customer)
        active_list = self.repository.list_by_status(CustomerStatus.ACTIVE)

        self.assertEqual(len(active_list), 1)
        self.assertEqual(self.repository.count_by_status(CustomerStatus.ACTIVE), 1)
        self.assertEqual(self.repository.count_by_status(CustomerStatus.INACTIVE), 0)
