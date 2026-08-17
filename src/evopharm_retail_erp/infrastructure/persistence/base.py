"""DeclarativeBase root for Infrastructure ORM models."""
from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base class for all Infrastructure ORM mappings."""
