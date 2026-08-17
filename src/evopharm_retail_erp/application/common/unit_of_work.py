"""Application-layer Unit of Work abstraction interface.

Defines the transactional boundary contract for use case orchestration.
This protocol contains zero database or ORM implementation details — concrete persistence adapters
(e.g., SQLAlchemy UnitOfWork) live exclusively in the Infrastructure layer.
"""
from __future__ import annotations

from types import TracebackType
from typing import Protocol, Self, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.customer import CustomerRepository
    from ...domain.inventory import InventoryRepository
    from ...domain.invoice import InvoiceRepository
    from ...domain.medicine import MedicineRepository
    from ...domain.purchase import PurchaseRepository
    from ...domain.sales import SaleRepository
    from ...domain.supplier import SupplierRepository


class UnitOfWork(Protocol):
    """Protocol defining the asynchronous Unit of Work transaction boundary."""

    medicines: MedicineRepository
    inventory: InventoryRepository
    purchases: PurchaseRepository
    sales: SaleRepository
    customers: CustomerRepository
    suppliers: SupplierRepository
    invoices: InvoiceRepository

    async def __aenter__(self) -> Self:
        """Enter the transactional unit of work scope."""
        ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the transactional scope, performing automatic rollback on unhandled errors."""
        ...

    async def commit(self) -> None:
        """Commit all aggregate persistence modifications made within this unit of work."""
        ...

    async def rollback(self) -> None:
        """Rollback all pending aggregate persistence modifications within this unit of work."""
        ...
