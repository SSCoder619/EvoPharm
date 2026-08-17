"""Global configuration for the EvoPharm Engineering + V&V Toolkit."""

from pathlib import Path

# Project paths
PROJECT_NAME = "EvoPharm"

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
PACKAGE_DIR = SRC_DIR / "evopharm_retail_erp"

DOMAIN_DIR = PACKAGE_DIR / "domain"
APP_DIR = PACKAGE_DIR / "application"
INFRA_DIR = PACKAGE_DIR / "infrastructure"
PRES_DIR = PACKAGE_DIR / "presentation"

TESTS_DIR = ROOT_DIR / "tests"
TOOLS_DIR = ROOT_DIR / "tools"
REPORTS_DIR = ROOT_DIR / "reports"

# Ignored directories for traversal
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
    "alembic",
}

IGNORE_FILES = {
    "__init__.py",
}

# Domain layer structure
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

# Application layer structure
EXPECTED_APP_FILES = {
    "commands.py",
    "results.py",
    "exceptions.py",
    "services.py",
}

# Active Bounded Contexts
BOUNDED_CONTEXTS = {
    "medicine",
    "inventory",
    "purchase",
    "sales",
    "customer",
    "supplier",
    "invoice",
}

REPORT_WIDTH = 70