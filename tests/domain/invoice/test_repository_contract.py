"""Contract tests for Invoice repository port."""
from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
from unittest import TestCase
from uuid import uuid4

from evopharm_retail_erp.domain.invoice import (
    Invoice,
    InvoiceId,
    InvoiceNumber,
    InvoiceRepository,
    InvoiceStatus,
    SaleReference,
)


class InMemoryInvoiceRepository(InvoiceRepository):
    """In-memory stub implementing InvoiceRepository contract for testing."""

    def __init__(self) -> None:
        self._store: dict[InvoiceId, Invoice] = {}

    def add(self, invoice: Invoice) -> None:
        if invoice.id in self._store:
            raise ValueError("Invoice already exists")
        self._store[invoice.id] = deepcopy(invoice)

    def save(self, invoice: Invoice) -> None:
        if invoice.id not in self._store:
            raise KeyError("Invoice not found")
        self._store[invoice.id] = deepcopy(invoice)

    def get_by_id(self, invoice_id: InvoiceId) -> Invoice | None:
        item = self._store.get(invoice_id)
        return deepcopy(item) if item else None

    def get_by_number(self, number: InvoiceNumber) -> Invoice | None:
        for item in self._store.values():
            if item.number == number:
                return deepcopy(item)
        return None

    def find_by_sale_reference(
        self, sale_reference: SaleReference
    ) -> Invoice | None:
        for item in self._store.values():
            if item.sale_reference and item.sale_reference.sale_id == sale_reference.sale_id:
                return deepcopy(item)
        return None

    def list_by_status(
        self, status: InvoiceStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Invoice]:
        return [deepcopy(item) for item in self._store.values() if item.status == status]

    def count_by_status(self, status: InvoiceStatus) -> int:
        return sum(1 for item in self._store.values() if item.status == status)

    def exists(self, invoice_id: InvoiceId) -> bool:
        return invoice_id in self._store

    def exists_number(self, number: InvoiceNumber) -> bool:
        return any(item.number == number for item in self._store.values())


class InvoiceRepositoryContractTests(TestCase):
    def setUp(self) -> None:
        self.repository = InMemoryInvoiceRepository()
        self.sale_ref = SaleReference(sale_id=uuid4(), sale_invoice_number="SALE-001")
        self.invoice = Invoice.create(
            number=InvoiceNumber("INV-2026-00001"),
            sale_reference=self.sale_ref,
        )

    def test_add_and_get_by_id(self) -> None:
        self.repository.add(self.invoice)
        retrieved = self.repository.get_by_id(self.invoice.id)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved, self.invoice)
        self.assertTrue(self.repository.exists(self.invoice.id))

    def test_get_by_number_and_exists_number(self) -> None:
        self.repository.add(self.invoice)
        retrieved = self.repository.get_by_number(self.invoice.number)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.number, self.invoice.number)
        self.assertTrue(self.repository.exists_number(self.invoice.number))

    def test_find_by_sale_reference(self) -> None:
        self.repository.add(self.invoice)
        retrieved = self.repository.find_by_sale_reference(self.sale_ref)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.sale_reference.sale_id, self.sale_ref.sale_id)

    def test_list_and_count_by_status(self) -> None:
        self.repository.add(self.invoice)
        draft_list = self.repository.list_by_status(InvoiceStatus.DRAFT)

        self.assertEqual(len(draft_list), 1)
        self.assertEqual(self.repository.count_by_status(InvoiceStatus.DRAFT), 1)
        self.assertEqual(self.repository.count_by_status(InvoiceStatus.ISSUED), 0)
