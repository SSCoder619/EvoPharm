"""SQLAlchemy engine creation for SQLite."""

from collections.abc import Mapping
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, make_url

from evopharm_retail_erp.infrastructure.database.configuration import DatabaseConfiguration


class DatabaseEngineFactory:
    """Creates configured SQLite engines without initializing schema."""

    @staticmethod
    def create(configuration: DatabaseConfiguration) -> Engine:
        """Create an engine for a validated SQLite URL."""

        url = make_url(configuration.url)
        if url.get_backend_name() != "sqlite":
            message = "EvoPharm database configuration must use SQLite."
            raise ValueError(message)

        connect_arguments: Mapping[str, Any] = {"check_same_thread": False}
        return create_engine(
            url,
            connect_args=connect_arguments,
            echo=configuration.echo,
            future=True,
            pool_pre_ping=configuration.pool_pre_ping,
        )
