"""Contract tests for Supplier repository port."""
from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
from unittest import TestCase

from evopharm_retail_erp.domain.supplier import (
    GSTIN,
    PAN,
    PhoneNumber,
    Supplier,
    SupplierCode,
    SupplierId,
    SupplierName,
    SupplierRepository,
    SupplierStatus,
)


class InMemorySupplierRepository(SupplierRepository):
    """In-memory stub implementing SupplierRepository contract for testing."""

    def __init__(self) -> None:
        self._store: dict[SupplierId, Supplier] = {}

    def add(self, supplier: Supplier) -> None:
        if supplier.id in self._store:
            raise ValueError("Supplier already exists")
        self._store[supplier.id] = deepcopy(supplier)

    def save(self, supplier: Supplier) -> None:
        if supplier.id not in self._store:
            raise KeyError("Supplier not found")
        self._store[supplier.id] = deepcopy(supplier)

    def get_by_id(self, supplier_id: SupplierId) -> Supplier | None:
        item = self._store.get(supplier_id)
        return deepcopy(item) if item else None

    def get_by_code(self, code: SupplierCode) -> Supplier | None:
        for item in self._store.values():
            if item.code == code:
                return deepcopy(item)
        return None

    def get_by_gstin(self, gstin: GSTIN) -> Supplier | None:
        for item in self._store.values():
            if item.gstin == gstin:
                return deepcopy(item)
        return None

    def list_by_status(
        self, status: SupplierStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Supplier]:
        return [deepcopy(item) for item in self._store.values() if item.status == status]

    def count_by_status(self, status: SupplierStatus) -> int:
        return sum(1 for item in self._store.values() if item.status == status)

    def exists(self, supplier_id: SupplierId) -> bool:
        return supplier_id in self._store

    def exists_code(self, code: SupplierCode) -> bool:
        return any(item.code == code for item in self._store.values())


class SupplierRepositoryContractTests(TestCase):
    def setUp(self) -> None:
        self.repository = InMemorySupplierRepository()
        self.supplier = Supplier.register(
            name=SupplierName("MedLife Supply"),
            phone=PhoneNumber("+919777766666"),
            code=SupplierCode("SUP-101"),
            gstin=GSTIN("29ABCDE1234F1Z5"),
            pan=PAN("ABCDE1234F"),
        )

    def test_add_and_get_by_id(self) -> None:
        self.repository.add(self.supplier)
        retrieved = self.repository.get_by_id(self.supplier.id)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved, self.supplier)
        self.assertTrue(self.repository.exists(self.supplier.id))

    def test_get_by_code_and_exists_code(self) -> None:
        self.repository.add(self.supplier)
        retrieved = self.repository.get_by_code(self.supplier.code)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.code, self.supplier.code)
        self.assertTrue(self.repository.exists_code(self.supplier.code))

    def test_get_by_gstin(self) -> None:
        self.repository.add(self.supplier)
        retrieved = self.repository.get_by_gstin(self.supplier.gstin)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.gstin, self.supplier.gstin)

    def test_list_and_count_by_status(self) -> None:
        self.repository.add(self.supplier)
        active_list = self.repository.list_by_status(SupplierStatus.ACTIVE)

        self.assertEqual(len(active_list), 1)
        self.assertEqual(self.repository.count_by_status(SupplierStatus.ACTIVE), 1)
        self.assertEqual(self.repository.count_by_status(SupplierStatus.INACTIVE), 0)
