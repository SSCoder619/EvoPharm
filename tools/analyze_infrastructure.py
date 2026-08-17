"""Infrastructure layer analyzer for EvoPharm Retail ERP."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path

try:
    from config import INFRA_DIR
    from common import iter_python_files, print_header, print_section, safe_parse
except ImportError:
    from .config import INFRA_DIR
    from .common import iter_python_files, print_header, print_section, safe_parse


@dataclass
class InfrastructureCheckResult:
    status: str = "PASS"
    orm_models_count: int = 0
    repositories_count: int = 0
    has_database_config: bool = False
    has_unit_of_work: bool = False
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class InfrastructureAnalyzer:
    """Analyzes the Infrastructure layer for persistence adapters and ORM mappings."""

    def run(self) -> InfrastructureCheckResult:
        result = InfrastructureCheckResult()
        print_header("Infrastructure Layer Analysis")

        if not INFRA_DIR.is_dir():
            result.status = "FAIL"
            result.violations.append(f"Infrastructure directory missing: {INFRA_DIR}")
            return result

        db_cfg = INFRA_DIR / "database" / "config.py"
        uow_file = INFRA_DIR / "unit_of_work" / "sqlalchemy.py"

        result.has_database_config = db_cfg.is_file()
        result.has_unit_of_work = uow_file.is_file()

        models_dir = INFRA_DIR / "persistence" / "models"
        if models_dir.is_dir():
            for m_file in iter_python_files(models_dir):
                tree = safe_parse(m_file)
                if tree:
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef) and any(
                            isinstance(b, ast.Name) and b.id == "Base" for b in node.bases
                        ):
                            result.orm_models_count += 1

        repos_dir = INFRA_DIR / "repositories"
        if repos_dir.is_dir():
            for r_file in iter_python_files(repos_dir):
                tree = safe_parse(r_file)
                if tree:
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef) and "Repository" in node.name:
                            result.repositories_count += 1

        for py_file in iter_python_files(INFRA_DIR):
            self._check_file_imports(py_file, result)

        if result.violations:
            result.status = "FAIL"
        elif result.warnings:
            result.status = "WARN"
        else:
            result.status = "PASS"

        print_section("Infrastructure Summary")
        print(f"Database Configuration Present: {result.has_database_config}")
        print(f"Unit of Work Present:          {result.has_unit_of_work}")
        print(f"ORM Models Discovered:         {result.orm_models_count}")
        print(f"Repository Adapters Discovered: {result.repositories_count}")
        print(f"Status:                        [{result.status}]")

        return result

    def _check_file_imports(self, py_file: Path, result: InfrastructureCheckResult) -> None:
        tree = safe_parse(py_file)
        if tree is None:
            return
        rel_path = py_file.relative_to(INFRA_DIR.parent.parent)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mod = getattr(node, "module", "") or ""
                if "tools" in mod.lower():
                    result.violations.append(f"{rel_path}: Production code illegally imports tools ({mod})")


def run() -> InfrastructureCheckResult:
    """Module entry point."""
    return InfrastructureAnalyzer().run()


if __name__ == "__main__":
    run()
