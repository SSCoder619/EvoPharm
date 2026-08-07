"""
Project tree utilities.
"""

from __future__ import annotations

from pathlib import Path

from config import IGNORE_DIRECTORIES


def build_tree(root: Path, indent: str = "") -> None:

    entries = sorted(root.iterdir())

    for entry in entries:

        if entry.name in IGNORE_DIRECTORIES:
            continue

        print(f"{indent}{entry.name}")

        if entry.is_dir():
            build_tree(entry, indent + "    ")