"""
Global configuration for the EvoPharm Architecture Analyzer.
"""

from pathlib import Path

# ---------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------

PROJECT_NAME = "EvoPharm"

ROOT_DIR = Path(__file__).resolve().parent.parent

SRC_DIR = ROOT_DIR / "src"

DOMAIN_DIR = SRC_DIR / "evopharm_retail_erp" / "domain"

TESTS_DIR = ROOT_DIR / "tests"

TOOLS_DIR = ROOT_DIR / "tools"

REPORTS_DIR = ROOT_DIR / "reports"

# ---------------------------------------------------------------------
# Ignored directories
# ---------------------------------------------------------------------

IGNORE_DIRECTORIES = {
    "__pycache__",
    ".git",
    ".idea",
    ".vscode",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
}

# ---------------------------------------------------------------------
# Ignored files
# ---------------------------------------------------------------------

IGNORE_FILES = {
    "__init__.py",
}

# ---------------------------------------------------------------------
# Expected files inside every bounded context
# ---------------------------------------------------------------------

EXPECTED_DOMAIN_FILES = {
    "entities.py",
    "value_objects.py",
    "enums.py",
    "exceptions.py",
    "interfaces.py",
}

OPTIONAL_DOMAIN_FILES = {
    "services.py",
    "specifications.py",
    "domain_events.py",
    "policies.py",
}

# ---------------------------------------------------------------------
# Valid bounded contexts
# ---------------------------------------------------------------------

BOUNDED_CONTEXTS = {
    "medicine",
    "inventory",
    "supplier",
    "customer",
    "purchase",
    "sales",
    "invoice",
    "billing",
    "user",
}

# ---------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------

REPORT_WIDTH = 70