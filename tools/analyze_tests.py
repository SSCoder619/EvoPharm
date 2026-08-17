"""Test suite analyzer and pytest subprocess runner for EvoPharm Retail ERP."""

from __future__ import annotations

import ast
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    from config import ROOT_DIR, TESTS_DIR
    from common import iter_python_files, print_header, print_section, safe_parse
except ImportError:
    from .config import ROOT_DIR, TESTS_DIR
    from .common import iter_python_files, print_header, print_section, safe_parse


@dataclass
class TestCheckResult:
    status: str = "PASS"
    test_files_count: int = 0
    test_functions_count: int = 0
    test_classes_count: int = 0
    pytest_executed: bool = False
    pytest_exit_code: int = 0
    pytest_output: str = ""
    warnings: list[str] = field(default_factory=list)


class TestAnalyzer:
    """Analyzes test suite structure and executes pytest via subprocess when requested."""

    def run(self, execute_pytest: bool = True) -> TestCheckResult:
        result = TestCheckResult()
        print_header("Test Suite Analysis")

        self._discover_tests(result)

        if execute_pytest:
            self._run_pytest_subprocess(result)

        if result.pytest_executed and result.pytest_exit_code != 0:
            result.status = "FAIL"
        elif result.warnings:
            result.status = "WARN"
        else:
            result.status = "PASS"

        print_section("Test Summary")
        print(f"Test Files Discovered:     {result.test_files_count}")
        print(f"Test Classes Discovered:   {result.test_classes_count}")
        print(f"Test Functions Discovered: {result.test_functions_count}")
        if result.pytest_executed:
            print(f"Pytest Execution Exit Code: {result.pytest_exit_code}")
        print(f"Status:                    [{result.status}]")

        return result

    def _discover_tests(self, result: TestCheckResult) -> None:
        if not TESTS_DIR.is_dir():
            result.warnings.append(f"Tests directory missing: {TESTS_DIR}")
            return

        for py_file in iter_python_files(TESTS_DIR):
            if not py_file.name.startswith("test_") and not py_file.name.endswith("_test.py"):
                continue

            result.test_files_count += 1
            tree = safe_parse(py_file)
            if tree is None:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and (node.name.startswith("Test") or node.name.endswith("Tests")):
                    result.test_classes_count += 1
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
                    result.test_functions_count += 1

    def _run_pytest_subprocess(self, result: TestCheckResult) -> None:
        """Execute pytest via subprocess using the current python executable."""
        env = os.environ.copy()
        src_path = str(ROOT_DIR / "src")
        existing_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{src_path};{existing_pythonpath}" if existing_pythonpath else src_path

        cmd = [sys.executable, "-m", "pytest", "--import-mode=importlib"]

        try:
            completed = subprocess.run(
                cmd,
                cwd=str(ROOT_DIR),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=60,
            )
            result.pytest_executed = True
            result.pytest_exit_code = completed.returncode
            result.pytest_output = completed.stdout
        except Exception as err:
            result.pytest_executed = False
            result.pytest_exit_code = 1
            result.warnings.append(f"Pytest execution failed to launch: {err}")


def run(execute_pytest: bool = True) -> TestCheckResult:
    """Module entry point."""
    return TestAnalyzer().run(execute_pytest=execute_pytest)


if __name__ == "__main__":
    run()
