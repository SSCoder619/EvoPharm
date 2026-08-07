"""Context-managed SQLAlchemy session infrastructure."""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


class SessionManager:
    """Creates transaction-scoped sessions for injected repositories."""

    def __init__(self, engine: Engine) -> None:
        """Create a session factory bound to the application engine."""

        self._session_factory = sessionmaker(
            bind=engine,
            autoflush=False,
            expire_on_commit=False,
        )

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Yield a session that commits on success and rolls back on failure."""

        session = self._session_factory()
        try:
            yield session
            session.commit()
        except BaseException:
            session.rollback()
            raise
        finally:
            session.close()
