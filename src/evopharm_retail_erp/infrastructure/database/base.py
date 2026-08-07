"""SQLAlchemy declarative metadata root for future entities."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base with no mapped entities."""

