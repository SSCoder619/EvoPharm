"""In-memory UnitOfWork helper for presentation API testing.

Allows testing API routers for all 7 bounded contexts without requiring
concrete database mappings for contexts not yet in SQLAlchemy.
"""
from __future__ import annotations

from typing import Dict, Optional, Sequence, Self
from uuid import UUID

from evopharm_retail_erp.application.common import UnitOfWork
from evopharm_retail_erp.domain.customer import (
    Customer,
    CustomerCode,
    CustomerId,
    CustomerRepository,
    CustomerStatus,
    CustomerType,
    PhoneNumber,
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
    InvoiceNumber as CommercialInvoiceNumber,
    InvoiceRepository,
    InvoiceStatus,
)
from evopharm_retail_erp.domain.medicine import MedicineBatchId, MedicineId
from evopharm_retail_erp.domain.purchase import (
    InvoiceReference,
    Purchase,
    PurchaseId,
    PurchaseOrderReference,
    PurchaseRepository,
    PurchaseStatus,
    ReceivingStatus,
    SupplierReference,
)
from evopharm_retail_erp.domain.sales import (
    CustomerReference,
    InvoiceNumber as SaleInvoiceNumber,
    Sale,
    SaleId,
    SaleRepository,
    SaleStatus,
)
from evopharm_retail_erp.domain.supplier import (
    GSTIN,
    Supplier,
    SupplierCode,
    SupplierId,
    SupplierRepository,
    SupplierStatus,
)
from evopharm_retail_erp.infrastructure.repositories.in_memory_medicine import (
    InMemoryMedicineRepository,
)


class InMemoryCustomerRepository(CustomerRepository):
    def __init__(self) -> None:
        self._data: Dict[UUID, Customer] = {}

    def add(self, customer: Customer) -> None:
        self._data[customer.id.value] = customer

    def save(self, customer: Customer) -> None:
        self._data[customer.id.value] = customer

    def get_by_id(self, customer_id: CustomerId) -> Customer | None:
        return self._data.get(customer_id.value)

    def get_by_code(self, code: CustomerCode) -> Customer | None:
        for c in self._data.values():
            if c.code and c.code.value == code.value:
                return c
        return None

    def get_by_phone(self, phone: PhoneNumber) -> Customer | None:
        for c in self._data.values():
            if c.phone.value == phone.value:
                return c
        return None

    def list_by_status(
        self, status: CustomerStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Customer]:
        matches = [c for c in self._data.values() if c.status == status]
        return tuple(matches[offset : offset + limit])

    def count_by_status(self, status: CustomerStatus) -> int:
        return sum(1 for c in self._data.values() if c.status == status)

    def exists(self, customer_id: CustomerId) -> bool:
        return customer_id.value in self._data


class InMemorySupplierRepository(SupplierRepository):
    def __init__(self) -> None:
        self._data: Dict[UUID, Supplier] = {}

    def add(self, supplier: Supplier) -> None:
        self._data[supplier.id.value] = supplier

    def save(self, supplier: Supplier) -> None:
        self._data[supplier.id.value] = supplier

    def get_by_id(self, supplier_id: SupplierId) -> Supplier | None:
        return self._data.get(supplier_id.value)

    def get_by_code(self, code: SupplierCode) -> Supplier | None:
        for s in self._data.values():
            if s.code and s.code.value == code.value:
                return s
        return None

    def get_by_gstin(self, gstin: GSTIN) -> Supplier | None:
        for s in self._data.values():
            if s.gstin and s.gstin.value == gstin.value:
                return s
        return None

    def list_by_status(
        self, status: SupplierStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Supplier]:
        matches = [s for s in self._data.values() if s.status == status]
        return tuple(matches[offset : offset + limit])

    def count_by_status(self, status: SupplierStatus) -> int:
        return sum(1 for s in self._data.values() if s.status == status)

    def exists(self, supplier_id: SupplierId) -> bool:
        return supplier_id.value in self._data

    def exists_code(self, code: SupplierCode) -> bool:
        return any(s.code and s.code.value == code.value for s in self._data.values())


class InMemoryPurchaseRepository(PurchaseRepository):
    def __init__(self) -> None:
        self._data: Dict[UUID, Purchase] = {}

    def add(self, purchase: Purchase) -> None:
        self._data[purchase.id.value] = purchase

    def save(self, purchase: Purchase) -> None:
        self._data[purchase.id.value] = purchase

    def get_by_id(self, purchase_id: PurchaseId) -> Purchase | None:
        return self._data.get(purchase_id.value)

    def get_by_order_reference(self, order_reference: PurchaseOrderReference) -> Purchase | None:
        for p in self._data.values():
            if p.order_reference.value == order_reference.value:
                return p
        return None

    def get_by_invoice_reference(self, invoice_reference: InvoiceReference) -> Purchase | None:
        for p in self._data.values():
            if p.invoice_reference and p.invoice_reference.value == invoice_reference.value:
                return p
        return None

    def list_by_supplier(
        self, supplier_id: SupplierReference | str | UUID, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Purchase]:
        return tuple(list(self._data.values())[offset : offset + limit])

    def list_by_status(
        self, status: PurchaseStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Purchase]:
        matches = [p for p in self._data.values() if p.purchase_status == status]
        return tuple(matches[offset : offset + limit])

    def list_by_receiving_status(
        self, receiving_status: ReceivingStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Purchase]:
        matches = [p for p in self._data.values() if p.receiving_status == receiving_status]
        return tuple(matches[offset : offset + limit])

    def count_by_status(self, status: PurchaseStatus) -> int:
        return sum(1 for p in self._data.values() if p.purchase_status == status)

    def exists(self, purchase_id: PurchaseId) -> bool:
        return purchase_id.value in self._data

    def exists_order_reference(self, order_reference: PurchaseOrderReference) -> bool:
        return any(p.order_reference.value == order_reference.value for p in self._data.values())


class InMemorySaleRepository(SaleRepository):
    def __init__(self) -> None:
        self._data: Dict[UUID, Sale] = {}

    def add(self, sale: Sale) -> None:
        self._data[sale.id.value] = sale

    def save(self, sale: Sale) -> None:
        self._data[sale.id.value] = sale

    def get_by_id(self, sale_id: SaleId) -> Sale | None:
        return self._data.get(sale_id.value)

    def get_by_invoice_number(self, invoice_number: SaleInvoiceNumber) -> Sale | None:
        for s in self._data.values():
            if s.invoice_number and s.invoice_number.value == invoice_number.value:
                return s
        return None

    def list_by_customer(
        self, customer: CustomerReference | str, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Sale]:
        return tuple(list(self._data.values())[offset : offset + limit])

    def list_by_status(
        self, status: SaleStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Sale]:
        matches = [s for s in self._data.values() if s.status == status]
        return tuple(matches[offset : offset + limit])

    def count_by_status(self, status: SaleStatus) -> int:
        return sum(1 for s in self._data.values() if s.status == status)

    def exists(self, sale_id: SaleId) -> bool:
        return sale_id.value in self._data

    def exists_invoice_number(self, invoice_number: SaleInvoiceNumber) -> bool:
        return any(s.invoice_number and s.invoice_number.value == invoice_number.value for s in self._data.values())


class InMemoryInvoiceRepository(InvoiceRepository):
    def __init__(self) -> None:
        self._data: Dict[UUID, Invoice] = {}

    def add(self, invoice: Invoice) -> None:
        self._data[invoice.id.value] = invoice

    def save(self, invoice: Invoice) -> None:
        self._data[invoice.id.value] = invoice

    def get_by_id(self, invoice_id: InvoiceId) -> Invoice | None:
        return self._data.get(invoice_id.value)

    def get_by_number(self, number: CommercialInvoiceNumber) -> Invoice | None:
        for inv in self._data.values():
            if inv.number.value == number.value:
                return inv
        return None

    def list_by_status(
        self, status: InvoiceStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Invoice]:
        matches = [inv for inv in self._data.values() if inv.status == status]
        return tuple(matches[offset : offset + limit])

    def count_by_status(self, status: InvoiceStatus) -> int:
        return sum(1 for inv in self._data.values() if inv.status == status)

    def exists(self, invoice_id: InvoiceId) -> bool:
        return invoice_id.value in self._data

    def exists_number(self, number: CommercialInvoiceNumber) -> bool:
        return any(inv.number.value == number.value for inv in self._data.values())


class InMemoryInventoryRepository(InventoryRepository):
    def __init__(self) -> None:
        self._data: Dict[UUID, Inventory] = {}

    def add(self, inventory: Inventory) -> None:
        self._data[inventory.id.value] = inventory

    def save(self, inventory: Inventory) -> None:
        self._data[inventory.id.value] = inventory

    def get_by_id(self, inventory_id: InventoryId) -> Inventory | None:
        return self._data.get(inventory_id.value)

    def get_by_batch_id(self, medicine_batch_id: MedicineBatchId) -> Inventory | None:
        for inv in self._data.values():
            if inv.medicine_batch_id.value == medicine_batch_id.value:
                return inv
        return None

    def list_by_medicine_id(
        self, medicine_id: MedicineId, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Inventory]:
        matches = [inv for inv in self._data.values() if inv.medicine_id.value == medicine_id.value]
        return tuple(matches[offset : offset + limit])

    def list_by_status(
        self, status: StockStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Inventory]:
        matches = [inv for inv in self._data.values() if inv.status == status]
        return tuple(matches[offset : offset + limit])

    def count_by_status(self, status: StockStatus) -> int:
        return sum(1 for inv in self._data.values() if inv.status == status)

    def exists(self, inventory_id: InventoryId) -> bool:
        return inventory_id.value in self._data


class InMemoryUnitOfWork(UnitOfWork):
    """In-memory UnitOfWork implementation for presentation testing."""

    def __init__(self) -> None:
        self._medicines = InMemoryMedicineRepository()
        self._inventory = InMemoryInventoryRepository()
        self._suppliers = InMemorySupplierRepository()
        self._purchases = InMemoryPurchaseRepository()
        self._customers = InMemoryCustomerRepository()
        self._sales = InMemorySaleRepository()
        self._invoices = InMemoryInvoiceRepository()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass

    @property
    def medicines(self):
        return self._medicines

    @property
    def medicine(self):
        return self._medicines

    @property
    def inventory(self):
        return self._inventory

    @property
    def suppliers(self):
        return self._suppliers

    @property
    def supplier(self):
        return self._suppliers

    @property
    def purchases(self):
        return self._purchases

    @property
    def purchase(self):
        return self._purchases

    @property
    def customers(self):
        return self._customers

    @property
    def customer(self):
        return self._customers

    @property
    def sales(self):
        return self._sales

    @property
    def sale(self):
        return self._sales

    @property
    def invoices(self):
        return self._invoices

    @property
    def invoice(self):
        return self._invoices
