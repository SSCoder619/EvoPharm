"""Static AST dependency analyzer for EvoPharm Retail ERP."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path

try:
    from config import PACKAGE_DIR
    from common import iter_python_files, print_header, print_section, safe_parse
except ImportError:
    from .config import PACKAGE_DIR
    from .common import iter_python_files, print_header, print_section, safe_parse


@dataclass
class DependencyCheckResult:
    status: str = "PASS"
    total_imports: int = 0
    external_imports: set[str] = field(default_factory=set)
    internal_imports: set[str] = field(default_factory=set)
    warnings: list[str] = field(default_factory=list)


class DependencyAnalyzer:
    """Performs static analysis of import statements and layer couplings."""

    def run(self) -> DependencyCheckResult:
        result = DependencyCheckResult()
        print_header("Dependency & Import Analysis")

        if not PACKAGE_DIR.is_dir():
            print(f"[WARN] Package directory missing: {PACKAGE_DIR}")
            result.status = "WARN"
            return result

        for py_file in iter_python_files(PACKAGE_DIR):
            tree = safe_parse(py_file)
            if tree is None:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        result.total_imports += 1
                        self._categorize_import(alias.name, result)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        result.total_imports += 1
                        self._categorize_import(node.module, result)

        if result.warnings:
            result.status = "WARN"
        else:
            result.status = "PASS"

        print_section("Dependency Summary")
        print(f"Total Import Statements: {result.total_imports}")
        print(f"Unique External Packages: {len(result.external_imports)}")
        print(f"Unique Internal Modules:  {len(result.internal_imports)}")
        print(f"Status:                   [{result.status}]")

        return result

    def _categorize_import(self, module_name: str, result: DependencyCheckResult) -> None:
        if module_name.startswith("evopharm_retail_erp") or module_name.startswith("."):
            result.internal_imports.add(module_name)
        else:
            top_level = module_name.split(".")[0]
            result.external_imports.add(top_level)


def run() -> DependencyCheckResult:
    """Module entry point."""
    return DependencyAnalyzer().run()


if __name__ == "__main__":
    run()
