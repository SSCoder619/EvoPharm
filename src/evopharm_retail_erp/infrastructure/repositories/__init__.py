"""Infrastructure repositories package and concrete adapters."""
from __future__ import annotations

from typing import Generic, TypeVar
from sqlalchemy.orm import Session

from .in_memory_medicine import InMemoryMedicineRepository
from .inventory import SqlAlchemyInventoryRepository
from .medicine import SqlAlchemyMedicineRepository
from .purchase import SqlAlchemyPurchaseRepository
from .supplier import SqlAlchemySupplierRepository

T = TypeVar("T")


class SqlAlchemyRepository(Generic[T]):
    """Base repository wrapper providing shared SQLAlchemy session access."""

    def __init__(self, session: Session) -> None:
        self.session = session


__all__ = [
    "SqlAlchemyRepository",
    "InMemoryMedicineRepository",
    "SqlAlchemyMedicineRepository",
    "SqlAlchemyInventoryRepository",
    "SqlAlchemySupplierRepository",
    "SqlAlchemyPurchaseRepository",
]
