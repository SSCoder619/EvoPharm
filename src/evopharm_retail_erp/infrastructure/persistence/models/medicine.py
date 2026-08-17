"""SQLAlchemy 2.x ORM models for the Medicine bounded context."""
from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base


class MedicineORM(Base):
    """ORM model representing the medicine_masters table."""

    __tablename__ = "medicine_masters"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    generic_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    composition_json: Mapped[str] = mapped_column(Text, nullable=False)
    manufacturer: Mapped[str] = mapped_column(String(200), nullable=False)
    hsn_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    pack_size: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_of_measure: Mapped[str] = mapped_column(String(50), nullable=False)
    dosage_form: Mapped[str] = mapped_column(String(50), nullable=False)
    schedule: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    storage_description: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    barcodes: Mapped[List[MedicineBarcodeORM]] = relationship(
        "MedicineBarcodeORM", back_populates="medicine", cascade="all, delete-orphan"
    )
    alternate_names: Mapped[List[MedicineAlternateNameORM]] = relationship(
        "MedicineAlternateNameORM", back_populates="medicine", cascade="all, delete-orphan"
    )
    batches: Mapped[List[MedicineBatchORM]] = relationship(
        "MedicineBatchORM", back_populates="medicine", cascade="all, delete-orphan"
    )


class MedicineBatchORM(Base):
    """ORM model representing physical medicine batches."""

    __tablename__ = "medicine_batches"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    medicine_id: Mapped[UUID] = mapped_column(
        ForeignKey("medicine_masters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    batch_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    manufacturing_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    received_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    quarantine_reason: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    adjustment_reason: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    recall_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    medicine: Mapped[MedicineORM] = relationship("MedicineORM", back_populates="batches")


class MedicineBarcodeORM(Base):
    """ORM model representing medicine registered barcode numbers."""

    __tablename__ = "medicine_barcodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    medicine_id: Mapped[UUID] = mapped_column(
        ForeignKey("medicine_masters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    barcode_value: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    barcode_type: Mapped[str] = mapped_column(String(50), nullable=False)

    medicine: Mapped[MedicineORM] = relationship("MedicineORM", back_populates="barcodes")


class MedicineAlternateNameORM(Base):
    """ORM model representing medicine alternate/brand lookup names."""

    __tablename__ = "medicine_alternate_names"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    medicine_id: Mapped[UUID] = mapped_column(
        ForeignKey("medicine_masters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    medicine: Mapped[MedicineORM] = relationship("MedicineORM", back_populates="alternate_names")
