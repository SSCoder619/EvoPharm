"""SQLAlchemy implementation of the PurchaseRepository protocol."""
from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

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
from ..persistence.mappers.purchase_mapper import orm_to_purchase, purchase_to_orm
from ..persistence.models.purchase import PurchaseORM


class SqlAlchemyPurchaseRepository(PurchaseRepository):
    """SQLAlchemy 2.x persistence adapter for Purchase aggregate root."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, purchase: Purchase) -> None:
        """Persist a newly created purchase order aggregate."""
        existing = self.session.get(PurchaseORM, purchase.id.value)
        if existing is not None:
            raise ValueError(f"Purchase {purchase.id} already exists")

        orm = purchase_to_orm(purchase)
        self.session.add(orm)
        self.session.flush()

    def save(self, purchase: Purchase) -> None:
        """Persist modifications to an existing purchase order aggregate with optimistic locking."""
        existing = self.session.get(PurchaseORM, purchase.id.value)
        if existing is None:
            raise KeyError(f"Purchase {purchase.id} does not exist")

        if purchase.version != existing.version + 1:
            raise ValueError(
                "Stale or invalid Purchase version; expected exactly one domain mutation"
            )

        new_orm = purchase_to_orm(purchase)
        self.session.merge(new_orm)
        self.session.flush()

    def get_by_id(self, purchase_id: PurchaseId) -> Purchase | None:
        """Retrieve a purchase order aggregate by its primary ID."""
        stmt = (
            select(PurchaseORM)
            .where(PurchaseORM.id == purchase_id.value)
            .options(joinedload(PurchaseORM.lines))
        )
        res = self.session.execute(stmt).unique().scalar_one_or_none()
        return orm_to_purchase(res) if res is not None else None

    def get_by_order_reference(
        self, order_reference: PurchaseOrderReference
    ) -> Purchase | None:
        """Retrieve a purchase order matching a unique order reference number."""
        stmt = (
            select(PurchaseORM)
            .where(PurchaseORM.order_reference == order_reference.value)
            .options(joinedload(PurchaseORM.lines))
        )
        res = self.session.execute(stmt).unique().scalar_one_or_none()
        return orm_to_purchase(res) if res is not None else None

    def get_by_invoice_reference(
        self, invoice_reference: InvoiceReference
    ) -> Purchase | None:
        """Retrieve a purchase order matching an attached commercial invoice reference."""
        stmt = (
            select(PurchaseORM)
            .where(PurchaseORM.invoice_reference == invoice_reference.value)
            .options(joinedload(PurchaseORM.lines))
        )
        res = self.session.execute(stmt).unique().scalar_one_or_none()
        return orm_to_purchase(res) if res is not None else None

    def list_by_supplier(
        self, supplier_id: SupplierReference | str | UUID, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Purchase]:
        """List purchase orders associated with a specific supplier."""
        if offset < 0 or limit < 0:
            raise ValueError("offset and limit must not be negative")

        target_uuid: UUID
        if isinstance(supplier_id, SupplierReference):
            target_uuid = supplier_id.supplier_id
        elif isinstance(supplier_id, UUID):
            target_uuid = supplier_id
        else:
            target_uuid = UUID(str(supplier_id))

        stmt = (
            select(PurchaseORM)
            .where(PurchaseORM.supplier_id == target_uuid)
            .options(joinedload(PurchaseORM.lines))
            .offset(offset)
            .limit(limit)
        )
        rows = self.session.execute(stmt).unique().scalars().all()
        return tuple(orm_to_purchase(r) for r in rows)

    def list_by_status(
        self, status: PurchaseStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Purchase]:
        """List purchase orders matching a specific lifecycle status."""
        if offset < 0 or limit < 0:
            raise ValueError("offset and limit must not be negative")
        stmt = (
            select(PurchaseORM)
            .where(PurchaseORM.purchase_status == status.value)
            .options(joinedload(PurchaseORM.lines))
            .offset(offset)
            .limit(limit)
        )
        rows = self.session.execute(stmt).unique().scalars().all()
        return tuple(orm_to_purchase(r) for r in rows)

    def list_by_receiving_status(
        self, receiving_status: ReceivingStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Purchase]:
        """List purchase orders matching a specific receiving status."""
        if offset < 0 or limit < 0:
            raise ValueError("offset and limit must not be negative")
        stmt = (
            select(PurchaseORM)
            .where(PurchaseORM.receiving_status == receiving_status.value)
            .options(joinedload(PurchaseORM.lines))
            .offset(offset)
            .limit(limit)
        )
        rows = self.session.execute(stmt).unique().scalars().all()
        return tuple(orm_to_purchase(r) for r in rows)

    def count_by_status(self, status: PurchaseStatus) -> int:
        """Count total purchase orders in a given status."""
        stmt = select(func.count(PurchaseORM.id)).where(
            PurchaseORM.purchase_status == status.value
        )
        return self.session.execute(stmt).scalar() or 0

    def exists(self, purchase_id: PurchaseId) -> bool:
        """Check if a purchase order exists by ID."""
        stmt = select(func.count(PurchaseORM.id)).where(PurchaseORM.id == purchase_id.value)
        return (self.session.execute(stmt).scalar() or 0) > 0

    def exists_order_reference(self, order_reference: PurchaseOrderReference) -> bool:
        """Check if a purchase order reference number is already registered."""
        stmt = select(func.count(PurchaseORM.id)).where(
            PurchaseORM.order_reference == order_reference.value
        )
        return (self.session.execute(stmt).scalar() or 0) > 0
