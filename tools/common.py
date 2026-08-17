"""Shared utilities for the EvoPharm Engineering + V&V Toolkit."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterator

try:
    from config import IGNORE_DIRECTORIES, IGNORE_FILES
except ImportError:
    from .config import IGNORE_DIRECTORIES, IGNORE_FILES


def iter_python_files(root: Path) -> Iterator[Path]:
    """Recursively yield every Python source file under root."""
    if not root.exists():
        return
    for path in root.rglob("*.py"):
        if any(part in IGNORE_DIRECTORIES for part in path.parts):
            continue
        if path.name in IGNORE_FILES:
            continue
        yield path


def iter_subdirectories(root: Path) -> Iterator[Path]:
    """Yield immediate subdirectories excluding ignored folders."""
    if not root.exists():
        return
    for child in root.iterdir():
        if not child.is_dir():
            continue
        if child.name in IGNORE_DIRECTORIES:
            continue
        yield child


def read_text(path: Path) -> str:
    """Read a UTF-8 file."""
    return path.read_text(encoding="utf-8", errors="ignore")


def safe_parse(path: Path) -> ast.Module | None:
    """Parse a Python file. Returns None if parsing fails."""
    try:
        return ast.parse(read_text(path))
    except SyntaxError:
        return None


def iter_classes(tree: ast.AST):
    """Yield every class definition."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            yield node


def iter_functions(tree: ast.AST):
    """Yield every function definition."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield node


def iter_imports(tree: ast.AST):
    """Yield every import statement."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            yield node


def has_decorator(node: ast.ClassDef, decorator: str) -> bool:
    """True if class has a given decorator."""
    for dec in node.decorator_list:
        if isinstance(dec, ast.Name):
            if dec.id == decorator:
                return True
        if isinstance(dec, ast.Call):
            if isinstance(dec.func, ast.Name):
                if dec.func.id == decorator:
                    return True
    return False


def is_dataclass(node: ast.ClassDef) -> bool:
    return has_decorator(node, "dataclass")


def class_names(tree: ast.AST) -> list[str]:
    return [c.name for c in iter_classes(tree)]


def function_names(tree: ast.AST) -> list[str]:
    return [f.name for f in iter_functions(tree)]


def print_header(title: str, width: int = 70) -> None:
    print("\n" + "=" * width)
    print(title.center(width))
    print("=" * width)


def print_section(title: str, width: int = 70) -> None:
    print("\n" + title)
    print("-" * width)


def plural(value: int, word: str) -> str:
    if value == 1:
        return f"{value} {word}"
    return f"{value} {word}s"