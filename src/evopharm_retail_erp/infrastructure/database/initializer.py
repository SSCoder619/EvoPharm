"""Database initialization boundary with no schema definition."""

from sqlalchemy.engine import Engine


class DatabaseInitializer:
    """Database lifecycle contract."""

    engine: Engine
