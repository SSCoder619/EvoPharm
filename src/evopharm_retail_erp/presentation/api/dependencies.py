"""Dependency Injection providers for the FastAPI presentation layer.

Adapts Application Services and UnitOfWork boundaries cleanly for HTTP endpoints.
Does NOT import ORM models or concrete repositories directly into routes.
"""
from __future__ import annotations

from typing import AsyncGenerator
from fastapi import Depends

from evopharm_retail_erp.application.common import UnitOfWork
from evopharm_retail_erp.application.customer import CustomerApplicationService
from evopharm_retail_erp.application.inventory import InventoryApplicationService
from evopharm_retail_erp.application.invoice import InvoiceApplicationService
from evopharm_retail_erp.application.medicine.commands import RegisterMedicineCommand
from evopharm_retail_erp.application.medicine.services import RegisterMedicineService
from evopharm_retail_erp.application.purchase import PurchaseApplicationService
from evopharm_retail_erp.application.sales import SalesApplicationService
from evopharm_retail_erp.application.supplier import SupplierApplicationService
from evopharm_retail_erp.infrastructure.database.config import get_database_config
from evopharm_retail_erp.infrastructure.database.session import (
    create_db_engine,
    create_session_factory,
)
from evopharm_retail_erp.infrastructure.unit_of_work import SqlAlchemyUnitOfWork

# Default database session factory singleton
_engine = None
_session_factory = None


def get_session_factory():
    global _engine, _session_factory
    if _session_factory is None:
        cfg = get_database_config()
        _engine = create_db_engine(cfg)
        _session_factory = create_session_factory(_engine)
    return _session_factory


async def get_uow() -> AsyncGenerator[UnitOfWork, None]:
    """Dependency provider yielding a UnitOfWork instance."""
    sf = get_session_factory()
    uow = SqlAlchemyUnitOfWork(sf)
    yield uow


def get_inventory_service(uow: UnitOfWork = Depends(get_uow)) -> InventoryApplicationService:
    return InventoryApplicationService(uow)


def get_purchase_service(uow: UnitOfWork = Depends(get_uow)) -> PurchaseApplicationService:
    return PurchaseApplicationService(uow)


def get_sale_service(uow: UnitOfWork = Depends(get_uow)) -> SalesApplicationService:
    return SalesApplicationService(uow)


def get_customer_service(uow: UnitOfWork = Depends(get_uow)) -> CustomerApplicationService:
    return CustomerApplicationService(uow)


def get_supplier_service(uow: UnitOfWork = Depends(get_uow)) -> SupplierApplicationService:
    return SupplierApplicationService(uow)


def get_invoice_service(uow: UnitOfWork = Depends(get_uow)) -> InvoiceApplicationService:
    return InvoiceApplicationService(uow)
