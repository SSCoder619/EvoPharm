"""SQLAlchemy implementation of the SupplierRepository protocol."""
from __future__ import annotations

from collections.abc import Sequence
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from evopharm_retail_erp.domain.supplier import (
    GSTIN,
    Supplier,
    SupplierCode,
    SupplierId,
    SupplierRepository,
    SupplierStatus,
)
from ..persistence.mappers.supplier_mapper import orm_to_supplier, supplier_to_orm
from ..persistence.models.supplier import SupplierORM


class SqlAlchemySupplierRepository(SupplierRepository):
    """SQLAlchemy 2.x persistence adapter for Supplier aggregate root."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, supplier: Supplier) -> None:
        """Persist a newly registered supplier aggregate."""
        existing = self.session.get(SupplierORM, supplier.id.value)
        if existing is not None:
            raise ValueError(f"Supplier {supplier.id} already exists")

        orm = supplier_to_orm(supplier)
        self.session.add(orm)
        self.session.flush()

    def save(self, supplier: Supplier) -> None:
        """Persist modifications to an existing supplier aggregate with optimistic locking."""
        existing = self.session.get(SupplierORM, supplier.id.value)
        if existing is None:
            raise KeyError(f"Supplier {supplier.id} does not exist")

        if supplier.version != existing.version + 1:
            raise ValueError(
                "Stale or invalid Supplier version; expected exactly one domain mutation"
            )

        new_orm = supplier_to_orm(supplier)
        self.session.merge(new_orm)
        self.session.flush()

    def get_by_id(self, supplier_id: SupplierId) -> Supplier | None:
        """Retrieve a supplier aggregate by its primary ID."""
        orm = self.session.get(SupplierORM, supplier_id.value)
        return orm_to_supplier(orm) if orm is not None else None

    def get_by_code(self, code: SupplierCode) -> Supplier | None:
        """Retrieve a supplier aggregate by unique supplier code."""
        stmt = select(SupplierORM).where(SupplierORM.code == code.value)
        orm = self.session.execute(stmt).scalar_one_or_none()
        return orm_to_supplier(orm) if orm is not None else None

    def get_by_gstin(self, gstin: GSTIN) -> Supplier | None:
        """Retrieve a supplier aggregate by GSTIN compliance identifier."""
        stmt = select(SupplierORM).where(SupplierORM.gstin == gstin.value)
        orm = self.session.execute(stmt).scalar_one_or_none()
        return orm_to_supplier(orm) if orm is not None else None

    def list_by_status(
        self, status: SupplierStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Supplier]:
        """List supplier aggregates matching a specific status."""
        if offset < 0 or limit < 0:
            raise ValueError("offset and limit must not be negative")
        stmt = (
            select(SupplierORM)
            .where(SupplierORM.status == status.value)
            .offset(offset)
            .limit(limit)
        )
        rows = self.session.execute(stmt).scalars().all()
        return tuple(orm_to_supplier(r) for r in rows)

    def count_by_status(self, status: SupplierStatus) -> int:
        """Count total supplier records in a given status."""
        stmt = select(func.count(SupplierORM.id)).where(SupplierORM.status == status.value)
        return self.session.execute(stmt).scalar() or 0

    def exists(self, supplier_id: SupplierId) -> bool:
        """Check if a supplier exists by ID."""
        stmt = select(func.count(SupplierORM.id)).where(SupplierORM.id == supplier_id.value)
        return (self.session.execute(stmt).scalar() or 0) > 0

    def exists_code(self, code: SupplierCode) -> bool:
        """Check if a supplier code is already registered."""
        stmt = select(func.count(SupplierORM.id)).where(SupplierORM.code == code.value)
        return (self.session.execute(stmt).scalar() or 0) > 0
