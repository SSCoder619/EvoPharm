"""Unit tests for Infrastructure database session lifecycle."""
from __future__ import annotations

from unittest import TestCase

from sqlalchemy import text

from evopharm_retail_erp.infrastructure.database.config import DatabaseSettings
from evopharm_retail_erp.infrastructure.database.session import (
    create_db_engine,
    create_session_factory,
    session_scope,
)


class SessionLifecycleTests(TestCase):
    def setUp(self) -> None:
        self.settings = DatabaseSettings(database_url="sqlite:///:memory:")
        self.engine = create_db_engine(self.settings)
        self.session_factory = create_session_factory(self.engine)

    def tearDown(self) -> None:
        self.engine.dispose()

    def test_session_commit_scope(self) -> None:
        with session_scope(self.session_factory) as session:
            res = session.execute(text("SELECT 1")).scalar()
            self.assertEqual(res, 1)

    def test_session_rollback_on_exception(self) -> None:
        with session_scope(self.session_factory) as session:
            session.execute(text("CREATE TABLE test_table (id INT)"))

        with self.assertRaises(RuntimeError):
            with session_scope(self.session_factory) as session:
                session.execute(text("INSERT INTO test_table VALUES (42)"))
                raise RuntimeError("Trigger rollback")

        with session_scope(self.session_factory) as session:
            count = session.execute(text("SELECT COUNT(*) FROM test_table")).scalar()
            self.assertEqual(count, 0)
