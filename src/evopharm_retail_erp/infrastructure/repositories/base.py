"""Shared repository infrastructure without data operations."""

from typing import Generic, TypeVar

from sqlalchemy.orm import Session


EntityType = TypeVar("EntityType")


class RepositoryBase(Generic[EntityType]):
    """Base class that receives a transaction-scoped SQLAlchemy session."""

    def __init__(self, session: Session) -> None:
        """Store the session supplied by the application composition root."""

        self._session = session
