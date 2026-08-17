"""SQLAlchemy Unit of Work implementation.

Implements the async UnitOfWork protocol defined in application/common/unit_of_work.py.
Manages database sessions, transactional boundaries (commit, rollback), and exposes repository boundaries.
"""
from __future__ import annotations

from types import TracebackType
from typing import Self
from sqlalchemy.orm import Session, sessionmaker

from evopharm_retail_erp.application.common import UnitOfWork
from evopharm_retail_erp.domain.customer import CustomerRepository
from evopharm_retail_erp.domain.inventory import InventoryRepository
from evopharm_retail_erp.domain.invoice import InvoiceRepository
from evopharm_retail_erp.domain.medicine import MedicineRepository
from evopharm_retail_erp.domain.purchase import PurchaseRepository
from evopharm_retail_erp.domain.sales import SaleRepository
from evopharm_retail_erp.domain.supplier import SupplierRepository
from ..repositories.inventory import SqlAlchemyInventoryRepository
from ..repositories.medicine import SqlAlchemyMedicineRepository
from ..repositories.purchase import SqlAlchemyPurchaseRepository
from ..repositories.supplier import SqlAlchemySupplierRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
    """SQLAlchemy implementation of the Application UnitOfWork protocol."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self.session: Session | None = None
        self._medicines: MedicineRepository | None = None
        self._inventory: InventoryRepository | None = None
        self._purchases: PurchaseRepository | None = None
        self._sales: SaleRepository | None = None
        self._customers: CustomerRepository | None = None
        self._suppliers: SupplierRepository | None = None
        self._invoices: InvoiceRepository | None = None

    async def __aenter__(self) -> Self:
        """Enter transaction scope and initialize session."""
        self.session = self._session_factory()
        self._medicines = SqlAlchemyMedicineRepository(self.session)
        self._inventory = SqlAlchemyInventoryRepository(self.session)
        self._suppliers = SqlAlchemySupplierRepository(self.session)
        self._purchases = SqlAlchemyPurchaseRepository(self.session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit transaction scope, rolling back on error and closing the session."""
        if exc_type is not None:
            await self.rollback()
        if self.session is not None:
            self.session.close()
            self.session = None
            self._medicines = None
            self._inventory = None
            self._suppliers = None
            self._purchases = None

    async def commit(self) -> None:
        """Commit all changes made in the current session transaction."""
        if self.session is not None:
            self.session.commit()

    async def rollback(self) -> None:
        """Rollback all changes made in the current session transaction."""
        if self.session is not None:
            self.session.rollback()

    # -- Repository Properties ------------------------------------------

    @property
    def medicines(self) -> MedicineRepository:
        if self._medicines is None:
            if self.session is not None:
                self._medicines = SqlAlchemyMedicineRepository(self.session)
            else:
                raise RuntimeError("UnitOfWork context has not been entered")
        return self._medicines

    @medicines.setter
    def medicines(self, value: MedicineRepository) -> None:
        self._medicines = value

    @property
    def medicine(self) -> MedicineRepository:
        return self.medicines

    @medicine.setter
    def medicine(self, value: MedicineRepository) -> None:
        self.medicines = value

    @property
    def inventory(self) -> InventoryRepository:
        if self._inventory is None:
            if self.session is not None:
                self._inventory = SqlAlchemyInventoryRepository(self.session)
            else:
                raise RuntimeError("UnitOfWork context has not been entered")
        return self._inventory

    @inventory.setter
    def inventory(self, value: InventoryRepository) -> None:
        self._inventory = value

    @property
    def suppliers(self) -> SupplierRepository:
        if self._suppliers is None:
            if self.session is not None:
                self._suppliers = SqlAlchemySupplierRepository(self.session)
            else:
                raise RuntimeError("UnitOfWork context has not been entered")
        return self._suppliers

    @suppliers.setter
    def suppliers(self, value: SupplierRepository) -> None:
        self._suppliers = value

    @property
    def supplier(self) -> SupplierRepository:
        return self.suppliers

    @supplier.setter
    def supplier(self, value: SupplierRepository) -> None:
        self.suppliers = value

    @property
    def purchases(self) -> PurchaseRepository:
        if self._purchases is None:
            if self.session is not None:
                self._purchases = SqlAlchemyPurchaseRepository(self.session)
            else:
                raise RuntimeError("UnitOfWork context has not been entered")
        return self._purchases

    @purchases.setter
    def purchases(self, value: PurchaseRepository) -> None:
        self._purchases = value

    @property
    def purchase(self) -> PurchaseRepository:
        return self.purchases

    @purchase.setter
    def purchase(self, value: PurchaseRepository) -> None:
        self.purchases = value

    @property
    def sales(self) -> SaleRepository:
        if self._sales is None:
            raise NotImplementedError("Sale SQLAlchemy repository will be mapped in a future phase")
        return self._sales

    @sales.setter
    def sales(self, value: SaleRepository) -> None:
        self._sales = value

    @property
    def sale(self) -> SaleRepository:
        return self.sales

    @sale.setter
    def sale(self, value: SaleRepository) -> None:
        self.sales = value

    @property
    def customers(self) -> CustomerRepository:
        if self._customers is None:
            raise NotImplementedError("Customer SQLAlchemy repository will be mapped in a future phase")
        return self._customers

    @customers.setter
    def customers(self, value: CustomerRepository) -> None:
        self._customers = value

    @property
    def customer(self) -> CustomerRepository:
        return self.customers

    @customer.setter
    def customer(self, value: CustomerRepository) -> None:
        self.customers = value

    @property
    def invoices(self) -> InvoiceRepository:
        if self._invoices is None:
            raise NotImplementedError("Invoice SQLAlchemy repository will be mapped in a future phase")
        return self._invoices

    @invoices.setter
    def invoices(self, value: InvoiceRepository) -> None:
        self._invoices = value

    @property
    def invoice(self) -> InvoiceRepository:
        return self.invoices

    @invoice.setter
    def invoice(self, value: InvoiceRepository) -> None:
        self.invoices = value
