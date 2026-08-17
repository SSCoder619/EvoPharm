"""SQLAlchemy 2.x ORM models for the Inventory bounded context."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base


class InventoryORM(Base):
    """ORM model representing stock inventory projections."""

    __tablename__ = "inventory_projections"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    medicine_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    medicine_batch_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    quantity_on_hand: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quantity_reserved: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    reorder_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    min_stock_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_stock_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    overstock_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    last_movement_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    movements: Mapped[List[StockMovementORM]] = relationship(
        "StockMovementORM", back_populates="inventory", cascade="all, delete-orphan"
    )


class StockMovementORM(Base):
    """ORM model representing immutable stock movement ledger entries."""

    __tablename__ = "stock_movements"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    inventory_id: Mapped[UUID] = mapped_column(
        ForeignKey("inventory_projections.id", ondelete="CASCADE"), nullable=False, index=True
    )
    medicine_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    medicine_batch_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    movement_type: Mapped[str] = mapped_column(String(50), nullable=False)
    direction: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    source_document_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    source_document_id: Mapped[Optional[UUID]] = mapped_column(nullable=True, index=True)
    source_document_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    reason: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    performed_by_user_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    inventory: Mapped[InventoryORM] = relationship("InventoryORM", back_populates="movements")
