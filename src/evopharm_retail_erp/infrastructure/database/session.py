"""SQLAlchemy engine and session factory setup."""
from __future__ import annotations

from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from .config import DatabaseSettings, get_database_config


def create_db_engine(settings: DatabaseSettings | None = None) -> Engine:
    """Create a configured SQLAlchemy sync Engine based on settings."""
    cfg = settings or get_database_config()
    connect_args = {}
    if cfg.is_sqlite:
        connect_args["check_same_thread"] = False

    return create_engine(
        cfg.database_url,
        connect_args=connect_args,
        echo=cfg.echo,
        pool_pre_ping=cfg.pool_pre_ping,
        future=True,
    )


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create a sessionmaker for sync sessions."""
    return sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )


@contextmanager
def session_scope(session_factory: sessionmaker[Session]) -> Generator[Session, None, None]:
    """Yield a transactional session scope committing on success and rolling back on error."""
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
