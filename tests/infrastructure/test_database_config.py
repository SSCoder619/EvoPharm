"""Unit tests for Infrastructure database configuration."""
from __future__ import annotations

import os
from unittest import TestCase
from unittest.mock import patch

from evopharm_retail_erp.infrastructure.database.config import (
    DatabaseSettings,
    get_database_config,
)


class DatabaseConfigTests(TestCase):
    def test_default_sqlite_settings(self) -> None:
        settings = DatabaseSettings()
        self.assertTrue(settings.is_sqlite)
        self.assertFalse(settings.is_postgresql)
        self.assertEqual(settings.database_url, "sqlite:///./evopharm.db")

    def test_postgresql_settings_property(self) -> None:
        settings = DatabaseSettings(database_url="postgresql+asyncpg://user:pass@localhost:5432/evopharm")
        self.assertFalse(settings.is_sqlite)
        self.assertTrue(settings.is_postgresql)

    @patch.dict(os.environ, {"DATABASE_URL": "sqlite:///:memory:", "DATABASE_ECHO": "true"})
    def test_get_database_config_from_environment(self) -> None:
        config = get_database_config()
        self.assertEqual(config.database_url, "sqlite:///:memory:")
        self.assertTrue(config.echo)
