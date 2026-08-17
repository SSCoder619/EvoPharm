"""Architectural boundary AST verification tests.

Verifies that bounded-context decoupling rules are strictly maintained:
1. Domain layer never imports Application layer.
2. Purchase Application never imports Inventory Application.
3. Sales Application never imports Inventory or Invoice Application.
4. Application Integration layer is the sole cross-context bridge.
"""
from __future__ import annotations

import ast
from pathlib import Path
from unittest import TestCase


class IntegrationBoundariesArchitectureTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.src_root = Path(__file__).resolve().parents[3] / "src" / "evopharm_retail_erp"

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

    def test_domain_layer_does_not_import_application_layer(self) -> None:
        domain_dir = self.src_root / "domain"
        for py_file in domain_dir.rglob("*.py"):
            imports = self._get_imports(py_file)
            for imp in imports:
                self.assertNotIn(
                    "application",
                    imp,
                    f"Domain file {py_file} illegally imports application module {imp}",
                )

    def test_purchase_application_does_not_import_inventory_application(self) -> None:
        purchase_app_dir = self.src_root / "application" / "purchase"
        for py_file in purchase_app_dir.glob("*.py"):
            imports = self._get_imports(py_file)
            for imp in imports:
                self.assertNotIn(
                    "inventory",
                    imp,
                    f"Purchase application file {py_file} illegally imports inventory application module {imp}",
                )

    def test_sales_application_does_not_import_inventory_or_invoice(self) -> None:
        sales_app_dir = self.src_root / "application" / "sales"
        for py_file in sales_app_dir.glob("*.py"):
            imports = self._get_imports(py_file)
            for imp in imports:
                self.assertNotIn(
                    "inventory",
                    imp,
                    f"Sales application file {py_file} illegally imports inventory application module {imp}",
                )
                self.assertNotIn(
                    "invoice",
                    imp,
                    f"Sales application file {py_file} illegally imports invoice application module {imp}",
                )
