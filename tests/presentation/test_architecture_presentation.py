"""Architecture boundary tests for Presentation layer."""
from __future__ import annotations

import ast
from pathlib import Path
from unittest import TestCase

SRC_DIR = Path(__file__).resolve().parent.parent.parent / "src"
PRES_DIR = SRC_DIR / "evopharm_retail_erp" / "presentation"
DOMAIN_DIR = SRC_DIR / "evopharm_retail_erp" / "domain"
APP_DIR = SRC_DIR / "evopharm_retail_erp" / "application"


class PresentationArchitectureTests(TestCase):
    def test_presentation_never_imports_sqlalchemy(self) -> None:
        """Presentation layer MUST NOT import SQLAlchemy directly."""
        for py_file in PRES_DIR.rglob("*.py"):
            tree = ast.parse(py_file.read_text(encoding="utf-8", errors="ignore"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertNotIn("sqlalchemy", alias.name.lower())
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.assertNotIn("sqlalchemy", node.module.lower())

    def test_presentation_never_imports_concrete_repositories(self) -> None:
        """Presentation routes MUST NOT import concrete SqlAlchemy repositories directly."""
        routes_dir = PRES_DIR / "api" / "routers"
        if routes_dir.is_dir():
            for py_file in routes_dir.rglob("*.py"):
                tree = ast.parse(py_file.read_text(encoding="utf-8", errors="ignore"))
                for node in ast.walk(tree):
                    mod = getattr(node, "module", "") or ""
                    self.assertNotIn("infrastructure.repositories", mod.lower())

    def test_domain_and_application_never_import_presentation(self) -> None:
        """Domain and Application MUST NOT import Presentation."""
        for layer_dir in (DOMAIN_DIR, APP_DIR):
            for py_file in layer_dir.rglob("*.py"):
                tree = ast.parse(py_file.read_text(encoding="utf-8", errors="ignore"))
                for node in ast.walk(tree):
                    mod = getattr(node, "module", "") or ""
                    self.assertNotIn("presentation", mod.lower())
