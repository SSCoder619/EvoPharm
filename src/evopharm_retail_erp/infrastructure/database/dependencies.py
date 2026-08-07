"""Database dependency bundle for dependency injection."""

from dataclasses import dataclass

from sqlalchemy.engine import Engine

from evopharm_retail_erp.infrastructure.database.configuration import DatabaseConfiguration
from evopharm_retail_erp.infrastructure.database.connection_manager import ConnectionManager
from evopharm_retail_erp.infrastructure.database.engine import DatabaseEngineFactory
from evopharm_retail_erp.infrastructure.database.session_manager import SessionManager


@dataclass(frozen=True, slots=True)
class DatabaseDependencies:
    """Database services assembled for application composition."""

    configuration: DatabaseConfiguration
    engine: Engine
    connections: ConnectionManager
    sessions: SessionManager

    @classmethod
    def create(cls, configuration: DatabaseConfiguration) -> "DatabaseDependencies":
        """Assemble database services without opening a connection or schema."""

        engine = DatabaseEngineFactory.create(configuration)
        return cls(
            configuration=configuration,
            engine=engine,
            connections=ConnectionManager(engine),
            sessions=SessionManager(engine),
        )
