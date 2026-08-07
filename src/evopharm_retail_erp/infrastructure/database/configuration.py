"""Database connection configuration."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DatabaseConfiguration:
    """Configuration required to create a SQLite database engine."""

    url: str
    echo: bool = False
    pool_pre_ping: bool = True
