"""Database connectivity initialization with no schema operations."""

from evopharm_retail_erp.infrastructure.database.connection_manager import ConnectionManager


class DatabaseInitializer:
    """Verifies database connectivity without creating tables or metadata."""

    def __init__(self, connection_manager: ConnectionManager) -> None:
        """Bind the initializer to managed connections."""

        self._connection_manager = connection_manager

    def initialize(self) -> None:
        """Open and close a connection without applying schema changes."""

        with self._connection_manager.connection():
            pass
