"""Architecture boundary validator for EvoPharm Retail ERP.

Verifies strict Clean Architecture layer separation and bounded-context decoupling using AST inspection.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path

try:
    from config import APP_DIR, DOMAIN_DIR, INFRA_DIR, PRES_DIR
    from common import iter_python_files, print_header, print_section, safe_parse
except ImportError:
    from .config import APP_DIR, DOMAIN_DIR, INFRA_DIR, PRES_DIR
    from .common import iter_python_files, print_header, print_section, safe_parse


@dataclass
class ArchitectureCheckResult:
    status: str = "PASS"  # PASS, WARN, FAIL
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    files_checked: int = 0


class ArchitectureAnalyzer:
    """Analyzes source files for forbidden architectural layer dependencies."""

    def run(self) -> ArchitectureCheckResult:
        result = ArchitectureCheckResult()
        print_header("Architecture Boundary Analysis")

        self._check_domain_layer(result)
        self._check_application_layer(result)
        self._check_infrastructure_layer(result)

        if result.violations:
            result.status = "FAIL"
        elif result.warnings:
            result.status = "WARN"
        else:
            result.status = "PASS"

        print_section("Architecture Summary")
        print(f"Files Checked: {result.files_checked}")
        print(f"Violations:    {len(result.violations)}")
        print(f"Warnings:      {len(result.warnings)}")
        print(f"Status:        [{result.status}]")

        if result.violations:
            print("\n[FAIL] CRITICAL VIOLATIONS:")
            for v in result.violations:
                print(f"  - {v}")

        if result.warnings:
            print("\n[WARN] WARNINGS:")
            for w in result.warnings:
                print(f"  - {w}")

        return result

    def _get_imports(self, file_path: Path) -> list[str]:
        tree = safe_parse(file_path)
        if tree is None:
            return []
        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports

    def _check_domain_layer(self, result: ArchitectureCheckResult) -> None:
        """Domain MUST NOT import application, infrastructure, presentation, sqlalchemy, or tools."""
        if not DOMAIN_DIR.is_dir():
            return

        for py_file in iter_python_files(DOMAIN_DIR):
            result.files_checked += 1
            imports = self._get_imports(py_file)
            rel_path = py_file.relative_to(DOMAIN_DIR.parent.parent)

            for imp in imports:
                imp_lower = imp.lower()
                if "infrastructure" in imp_lower:
                    result.violations.append(f"{rel_path}: Domain illegally imports infrastructure ({imp})")
                if "application" in imp_lower:
                    result.violations.append(f"{rel_path}: Domain illegally imports application ({imp})")
                if "presentation" in imp_lower:
                    result.violations.append(f"{rel_path}: Domain illegally imports presentation ({imp})")
                if "sqlalchemy" in imp_lower:
                    result.violations.append(f"{rel_path}: Domain illegally imports SQLAlchemy ({imp})")
                if "tools" in imp_lower:
                    result.violations.append(f"{rel_path}: Production code illegally imports tools ({imp})")

    def _check_application_layer(self, result: ArchitectureCheckResult) -> None:
        """Application MUST NOT import concrete infrastructure, sqlalchemy, or tools directly."""
        if not APP_DIR.is_dir():
            return

        for py_file in iter_python_files(APP_DIR):
            result.files_checked += 1
            imports = self._get_imports(py_file)
            rel_path = py_file.relative_to(APP_DIR.parent.parent)

            for imp in imports:
                imp_lower = imp.lower()
                if "infrastructure" in imp_lower:
                    result.violations.append(
                        f"{rel_path}: Application illegally imports concrete infrastructure ({imp})"
                    )
                if "sqlalchemy" in imp_lower:
                    result.violations.append(f"{rel_path}: Application illegally imports SQLAlchemy ({imp})")
                if "tools" in imp_lower:
                    result.violations.append(f"{rel_path}: Production code illegally imports tools ({imp})")

            # Cross-application module decoupling checks
            current_context = py_file.parent.name
            if current_context == "purchase" and any("inventory" in imp for imp in imports):
                result.violations.append(
                    f"{rel_path}: Purchase application illegally imports inventory application directly"
                )
            if current_context == "sales":
                if any("inventory" in imp for imp in imports):
                    result.violations.append(
                        f"{rel_path}: Sales application illegally imports inventory application directly"
                    )
                if any("invoice" in imp for imp in imports):
                    result.violations.append(
                        f"{rel_path}: Sales application illegally imports invoice application directly"
                    )

    def _check_infrastructure_layer(self, result: ArchitectureCheckResult) -> None:
        """Infrastructure may depend on Domain/Application, but MUST NOT import tools."""
        if not INFRA_DIR.is_dir():
            return

        for py_file in iter_python_files(INFRA_DIR):
            result.files_checked += 1
            imports = self._get_imports(py_file)
            rel_path = py_file.relative_to(INFRA_DIR.parent.parent)

            for imp in imports:
                if "tools" in imp.lower():
                    result.violations.append(f"{rel_path}: Production code illegally imports tools ({imp})")


def run() -> ArchitectureCheckResult:
    """Module entry point."""
    return ArchitectureAnalyzer().run()


if __name__ == "__main__":
    run()
