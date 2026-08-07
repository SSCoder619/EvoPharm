"""Managed database connection access."""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy.engine import Connection, Engine


class ConnectionManager:
    """Provides safely scoped SQLAlchemy connections."""

    def __init__(self, engine: Engine) -> None:
        """Bind the manager to an application engine."""

        self._engine = engine

    @contextmanager
    def connection(self) -> Generator[Connection, None, None]:
        """Yield a connection and close it when the context exits."""

        with self._engine.connect() as connection:
            yield connection
