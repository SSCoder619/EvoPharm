"""AST parser for the EvoPharm Architecture Analyzer."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path

try:
    from common import safe_parse
except ImportError:
    from .common import safe_parse


@dataclass(slots=True)
class FileInfo:
    path: Path

    classes: list[str] = field(default_factory=list)
    dataclasses: list[str] = field(default_factory=list)
    enums: list[str] = field(default_factory=list)
    protocols: list[str] = field(default_factory=list)
    exceptions: list[str] = field(default_factory=list)

    functions: list[str] = field(default_factory=list)
    async_functions: list[str] = field(default_factory=list)

    imports: list[str] = field(default_factory=list)
    has_module_docstring: bool = False


class PythonParser:

    def parse(self, file: Path) -> FileInfo:
        tree = safe_parse(file)
        info = FileInfo(path=file)

        if tree is None:
            return info

        info.has_module_docstring = ast.get_docstring(tree) is not None

        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    info.imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    info.imports.append(f"{module}.{alias.name}")
            elif isinstance(node, ast.FunctionDef):
                info.functions.append(node.name)
            elif isinstance(node, ast.AsyncFunctionDef):
                info.async_functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                info.classes.append(node.name)

                decorators = {
                    d.id
                    for d in node.decorator_list
                    if isinstance(d, ast.Name)
                }

                if "dataclass" in decorators:
                    info.dataclasses.append(node.name)

                for base in node.bases:
                    if isinstance(base, ast.Name):
                        if base.id == "Enum":
                            info.enums.append(node.name)
                        elif base.id == "Protocol":
                            info.protocols.append(node.name)
                        elif base.id.endswith("Error"):
                            info.exceptions.append(node.name)
                    elif isinstance(base, ast.Attribute):
                        if base.attr == "Enum":
                            info.enums.append(node.name)
                        elif base.attr == "Protocol":
                            info.protocols.append(node.name)

        return info