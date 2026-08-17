"""SQLAlchemy 2.x ORM models for the Purchase bounded context."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base


class PurchaseORM(Base):
    """ORM model representing the purchase_orders table."""

    __tablename__ = "purchase_orders"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    supplier_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    supplier_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    supplier_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    order_reference: Mapped[str] = mapped_column(String(100), nullable=False, index=True, unique=True)
    invoice_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    purchase_status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    receiving_status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    payment_status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    total_amount_paid: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    paid_currency: Mapped[str] = mapped_column(String(10), nullable=False, default="INR")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    lines: Mapped[List[PurchaseLineORM]] = relationship(
        "PurchaseLineORM", back_populates="purchase", cascade="all, delete-orphan"
    )


class PurchaseLineORM(Base):
    """ORM model representing line items within a purchase order."""

    __tablename__ = "purchase_order_lines"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    purchase_id: Mapped[UUID] = mapped_column(
        ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    medicine_id: Mapped[UUID] = mapped_column(nullable=False, index=True)

    ordered_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    received_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    unit_price_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    unit_price_currency: Mapped[str] = mapped_column(String(10), nullable=False, default="INR")

    discount_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("0.00"))
    discount_fixed_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    tax_rate_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("0.00"))

    status: Mapped[str] = mapped_column(String(50), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    purchase: Mapped[PurchaseORM] = relationship("PurchaseORM", back_populates="lines")
