"""Environment-driven database configuration for EvoPharm Retail ERP.

Supports development (SQLite) and production (PostgreSQL) database URLs sourced
from environment variables without hardcoded credentials.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DatabaseSettings:
    """Settings required to create a SQLAlchemy engine."""

    database_url: str = "sqlite:///./evopharm.db"
    echo: bool = False
    pool_pre_ping: bool = True

    @property
    def is_sqlite(self) -> bool:
        """Return True if the database URL targets SQLite."""
        return "sqlite" in self.database_url.lower()

    @property
    def is_postgresql(self) -> bool:
        """Return True if the database URL targets PostgreSQL."""
        return "postgresql" in self.database_url.lower() or "postgres" in self.database_url.lower()


def get_database_config() -> DatabaseSettings:
    """Load database settings from environment variables."""
    db_url = os.getenv("DATABASE_URL", "sqlite:///./evopharm.db")
    echo = os.getenv("DATABASE_ECHO", "false").lower() in ("true", "1", "yes")
    pool_pre_ping = os.getenv("DATABASE_POOL_PRE_PING", "true").lower() in ("true", "1", "yes")

    return DatabaseSettings(
        database_url=db_url,
        echo=echo,
        pool_pre_ping=pool_pre_ping,
    )
