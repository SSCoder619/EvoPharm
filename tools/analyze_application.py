"""Application layer structure and compliance analyzer for EvoPharm Retail ERP."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path

try:
    from config import APP_DIR, BOUNDED_CONTEXTS, EXPECTED_APP_FILES
    from common import iter_python_files, iter_subdirectories, print_header, print_section, safe_parse
except ImportError:
    from .config import APP_DIR, BOUNDED_CONTEXTS, EXPECTED_APP_FILES
    from .common import iter_python_files, iter_subdirectories, print_header, print_section, safe_parse


@dataclass
class ApplicationCheckResult:
    status: str = "PASS"
    contexts_found: int = 0
    commands_count: int = 0
    results_count: int = 0
    services_count: int = 0
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class ApplicationAnalyzer:
    """Analyzes the Application layer for use-case organization and architectural ports compliance."""

    def run(self) -> ApplicationCheckResult:
        result = ApplicationCheckResult()
        print_header("Application Layer Analysis")

        if not APP_DIR.is_dir():
            result.status = "FAIL"
            result.violations.append(f"Application directory missing: {APP_DIR}")
            return result

        subdirs = {d.name for d in iter_subdirectories(APP_DIR)}
        target_contexts = sorted(subdirs & BOUNDED_CONTEXTS)
        result.contexts_found = len(target_contexts)

        for ctx_name in target_contexts:
            ctx_path = APP_DIR / ctx_name
            self._analyze_app_context(ctx_name, ctx_path, result)

        for py_file in iter_python_files(APP_DIR):
            self._check_file_imports(py_file, result)

        if result.violations:
            result.status = "FAIL"
        elif result.warnings:
            result.status = "WARN"
        else:
            result.status = "PASS"

        print_section("Application Summary")
        print(f"Application Contexts:  {result.contexts_found}")
        print(f"Command DTO Classes:   {result.commands_count}")
        print(f"Result DTO Classes:    {result.results_count}")
        print(f"Application Services:  {result.services_count}")
        print(f"Status:                [{result.status}]")

        return result

    def _analyze_app_context(self, name: str, path: Path, result: ApplicationCheckResult) -> None:
        for expected_file in EXPECTED_APP_FILES:
            fpath = path / expected_file
            if not fpath.is_file():
                result.warnings.append(f"Application context {name} missing {expected_file}")

        for fname in ("commands.py", "results.py", "services.py"):
            fpath = path / fname
            if fpath.is_file():
                tree = safe_parse(fpath)
                if tree:
                    if fname == "commands.py":
                        result.commands_count += len([c for c in ast.walk(tree) if isinstance(c, ast.ClassDef)])
                    elif fname == "results.py":
                        result.results_count += len([c for c in ast.walk(tree) if isinstance(c, ast.ClassDef)])
                    elif fname == "services.py":
                        result.services_count += len(
                            [c for c in ast.walk(tree) if isinstance(c, ast.ClassDef) and "Service" in c.name]
                        )

    def _check_file_imports(self, py_file: Path, result: ApplicationCheckResult) -> None:
        tree = safe_parse(py_file)
        if tree is None:
            return
        rel_path = py_file.relative_to(APP_DIR.parent.parent)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mod = getattr(node, "module", "") or ""
                if "infrastructure" in mod.lower():
                    result.violations.append(
                        f"{rel_path}: Application illegally imports concrete infrastructure ({mod})"
                    )
                if "sqlalchemy" in mod.lower():
                    result.violations.append(f"{rel_path}: Application illegally imports SQLAlchemy ({mod})")


def run() -> ApplicationCheckResult:
    """Module entry point."""
    return ApplicationAnalyzer().run()


if __name__ == "__main__":
    run()
