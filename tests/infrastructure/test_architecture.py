"""Architectural AST boundary tests for Infrastructure layer.

Proves that:
1. Domain -> Infrastructure import = FORBIDDEN
2. Domain -> SQLAlchemy import = FORBIDDEN
3. Application -> SQLAlchemy import = FORBIDDEN
4. Application -> Infrastructure concrete repository = FORBIDDEN
"""
from __future__ import annotations

import ast
from pathlib import Path
from unittest import TestCase


class InfrastructureArchitectureTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.src_root = Path(__file__).resolve().parents[2] / "src" / "evopharm_retail_erp"

    def _get_imports(self, file_path: Path) -> list[str]:
        """Extract all imported module strings from a Python file using AST parsing."""
        with open(file_path, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports

    def test_domain_never_imports_infrastructure(self) -> None:
        domain_dir = self.src_root / "domain"
        for py_file in domain_dir.rglob("*.py"):
            imports = self._get_imports(py_file)
            for imp in imports:
                self.assertNotIn(
                    "infrastructure",
                    imp,
                    f"Domain file {py_file} illegally imports infrastructure module {imp}",
                )

    def test_domain_never_imports_sqlalchemy(self) -> None:
        domain_dir = self.src_root / "domain"
        for py_file in domain_dir.rglob("*.py"):
            imports = self._get_imports(py_file)
            for imp in imports:
                self.assertNotIn(
                    "sqlalchemy",
                    imp.lower(),
                    f"Domain file {py_file} illegally imports sqlalchemy module {imp}",
                )

    def test_application_never_imports_sqlalchemy(self) -> None:
        app_dir = self.src_root / "application"
        for py_file in app_dir.rglob("*.py"):
            imports = self._get_imports(py_file)
            for imp in imports:
                self.assertNotIn(
                    "sqlalchemy",
                    imp.lower(),
                    f"Application file {py_file} illegally imports sqlalchemy module {imp}",
                )

    def test_application_never_imports_concrete_infrastructure(self) -> None:
        app_dir = self.src_root / "application"
        for py_file in app_dir.rglob("*.py"):
            imports = self._get_imports(py_file)
            for imp in imports:
                self.assertNotIn(
                    "infrastructure",
                    imp,
                    f"Application file {py_file} illegally imports infrastructure module {imp}",
                )
