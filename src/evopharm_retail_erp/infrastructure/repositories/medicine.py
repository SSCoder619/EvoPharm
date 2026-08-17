"""SQLAlchemy implementation of the MedicineRepository protocol."""
from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from evopharm_retail_erp.domain.medicine import (
    Medicine,
    MedicineId,
    MedicineRepository,
    MedicineStatus,
)
from ..persistence.mappers.medicine_mapper import medicine_to_orm, orm_to_medicine
from ..persistence.models.medicine import (
    MedicineAlternateNameORM,
    MedicineBarcodeORM,
    MedicineORM,
)

if TYPE_CHECKING:
    pass


class SqlAlchemyMedicineRepository(MedicineRepository):
    """SQLAlchemy 2.x persistence adapter for Medicine aggregate root."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def _query(self):
        """Query helper with eager loading of child collections."""
        return self.session.query(MedicineORM).options(
            joinedload(MedicineORM.barcodes),
            joinedload(MedicineORM.alternate_names),
            joinedload(MedicineORM.batches),
        )

    def add(self, medicine: Medicine) -> None:
        """Persist a newly registered medicine master record."""
        existing = self.session.get(MedicineORM, medicine.id.value)
        if existing is not None:
            raise ValueError(f"Medicine {medicine.id} already exists")

        # Check duplicate barcode uniqueness
        for bc in medicine.barcodes:
            if self.exists_by_barcode(bc.value):
                raise ValueError("A medicine with one of these barcodes already exists")

        orm = medicine_to_orm(medicine)
        self.session.add(orm)
        self.session.flush()

    def save(self, medicine: Medicine) -> None:
        """Persist modifications to an existing medicine master record with optimistic locking."""
        existing = self.session.get(MedicineORM, medicine.id.value)
        if existing is None:
            raise KeyError(f"Medicine {medicine.id} does not exist")

        if medicine.version != existing.version + 1:
            raise ValueError(
                "Stale or invalid Medicine version; expected exactly one domain mutation"
            )

        # Merge updated state
        new_orm = medicine_to_orm(medicine)

        # Remove existing child rows to avoid orphan duplicates on merge
        self.session.query(MedicineBarcodeORM).filter_by(medicine_id=medicine.id.value).delete()
        self.session.query(MedicineAlternateNameORM).filter_by(medicine_id=medicine.id.value).delete()
        self.session.flush()

        self.session.merge(new_orm)
        self.session.flush()

    def get_by_id(self, medicine_id: MedicineId) -> Medicine | None:
        """Retrieve a medicine master record by unique identifier."""
        stmt = (
            select(MedicineORM)
            .where(MedicineORM.id == medicine_id.value)
            .options(
                joinedload(MedicineORM.barcodes),
                joinedload(MedicineORM.alternate_names),
                joinedload(MedicineORM.batches),
            )
        )
        res = self.session.execute(stmt).unique().scalar_one_or_none()
        return orm_to_medicine(res) if res is not None else None

    def get_by_barcode(self, barcode_value: str) -> Medicine | None:
        """Retrieve a medicine master record matching a barcode value."""
        cleaned = "".join(barcode_value.split())
        stmt = (
            select(MedicineORM)
            .join(MedicineBarcodeORM)
            .where(MedicineBarcodeORM.barcode_value == cleaned)
            .options(
                joinedload(MedicineORM.barcodes),
                joinedload(MedicineORM.alternate_names),
                joinedload(MedicineORM.batches),
            )
        )
        res = self.session.execute(stmt).unique().scalar_one_or_none()
        return orm_to_medicine(res) if res is not None else None

    def find_by_name(
        self, query: str, *, offset: int = 0, limit: int = 20
    ) -> Sequence[Medicine]:
        """Find medicine master records by brand or alternate name."""
        if offset < 0 or limit < 0:
            raise ValueError("offset and limit must not be negative")
        clean_query = "%" + " ".join(query.split()).casefold() + "%"

        stmt = (
            select(MedicineORM)
            .outerjoin(MedicineAlternateNameORM)
            .where(
                func.lower(MedicineORM.name).like(clean_query)
                | func.lower(MedicineAlternateNameORM.name).like(clean_query)
            )
            .options(
                joinedload(MedicineORM.barcodes),
                joinedload(MedicineORM.alternate_names),
                joinedload(MedicineORM.batches),
            )
            .order_by(func.lower(MedicineORM.name))
            .offset(offset)
            .limit(limit)
        )
        rows = self.session.execute(stmt).unique().scalars().all()
        return tuple(orm_to_medicine(row) for row in rows)

    def find_by_generic_name(self, generic_name: str) -> Sequence[Medicine]:
        """Find medicine master records matching a generic composition name."""
        clean_name = " ".join(generic_name.split()).casefold()
        stmt = (
            select(MedicineORM)
            .where(func.lower(MedicineORM.generic_name) == clean_name)
            .options(
                joinedload(MedicineORM.barcodes),
                joinedload(MedicineORM.alternate_names),
                joinedload(MedicineORM.batches),
            )
        )
        rows = self.session.execute(stmt).unique().scalars().all()
        return tuple(orm_to_medicine(row) for row in rows)

    def find_by_hsn_code(self, hsn_code: str) -> Sequence[Medicine]:
        """Find medicine master records with a matching HSN code."""
        clean_hsn = hsn_code.strip()
        stmt = (
            select(MedicineORM)
            .where(MedicineORM.hsn_code == clean_hsn)
            .options(
                joinedload(MedicineORM.barcodes),
                joinedload(MedicineORM.alternate_names),
                joinedload(MedicineORM.batches),
            )
        )
        rows = self.session.execute(stmt).unique().scalars().all()
        return tuple(orm_to_medicine(row) for row in rows)

    def list_by_status(
        self, status: MedicineStatus, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Medicine]:
        """List medicine master records matching a given status."""
        if offset < 0 or limit < 0:
            raise ValueError("offset and limit must not be negative")
        stmt = (
            select(MedicineORM)
            .where(MedicineORM.status == status.value)
            .options(
                joinedload(MedicineORM.barcodes),
                joinedload(MedicineORM.alternate_names),
                joinedload(MedicineORM.batches),
            )
            .order_by(func.lower(MedicineORM.name))
            .offset(offset)
            .limit(limit)
        )
        rows = self.session.execute(stmt).unique().scalars().all()
        return tuple(orm_to_medicine(row) for row in rows)

    def count_by_status(self, status: MedicineStatus) -> int:
        """Count total medicine master records in a given status."""
        stmt = select(func.count(MedicineORM.id)).where(MedicineORM.status == status.value)
        return self.session.execute(stmt).scalar() or 0

    def exists_by_barcode(self, barcode_value: str) -> bool:
        """Check if any medicine master record has the given barcode registered."""
        cleaned = "".join(barcode_value.split())
        stmt = select(func.count(MedicineBarcodeORM.id)).where(
            MedicineBarcodeORM.barcode_value == cleaned
        )
        count = self.session.execute(stmt).scalar() or 0
        return count > 0

    def exists_by_name(self, name: str) -> bool:
        """Check if any medicine master record has the given brand name."""
        clean_name = " ".join(name.split()).casefold()
        stmt = select(func.count(MedicineORM.id)).where(
            func.lower(MedicineORM.name) == clean_name
        )
        count = self.session.execute(stmt).scalar() or 0
        return count > 0
