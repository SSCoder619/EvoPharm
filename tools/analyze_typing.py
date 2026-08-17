"""AST-based typing analysis for EvoPharm Retail ERP."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field

try:
    from config import PACKAGE_DIR
    from common import iter_python_files, print_header, print_section, safe_parse
except ImportError:
    from .config import PACKAGE_DIR
    from .common import iter_python_files, print_header, print_section, safe_parse


@dataclass
class TypingCheckResult:
    status: str = "PASS"
    total_functions: int = 0
    annotated_functions: int = 0
    missing_return_annotations: int = 0
    any_uses_count: int = 0
    warnings: list[str] = field(default_factory=list)


class TypingAnalyzer:
    """Performs lightweight static AST analysis of type hints."""

    def run(self) -> TypingCheckResult:
        result = TypingCheckResult()
        print_header("Typing & Type Hint Analysis")

        if not PACKAGE_DIR.is_dir():
            result.status = "WARN"
            return result

        for py_file in iter_python_files(PACKAGE_DIR):
            tree = safe_parse(py_file)
            if tree is None:
                continue

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    result.total_functions += 1
                    if node.returns is not None:
                        result.annotated_functions += 1
                    else:
                        # __init__ missing return annotation is acceptable
                        if node.name != "__init__":
                            result.missing_return_annotations += 1

                elif isinstance(node, ast.Name) and node.id == "Any":
                    result.any_uses_count += 1

        if result.missing_return_annotations > 0 or result.any_uses_count > 0:
            result.status = "WARN"
        else:
            result.status = "PASS"

        coverage = (
            (result.annotated_functions / result.total_functions * 100)
            if result.total_functions > 0
            else 100.0
        )

        print_section("Typing Summary")
        print(f"Total Functions Checked:    {result.total_functions}")
        print(f"Annotated Functions:       {result.annotated_functions} ({coverage:.1f}%)")
        print(f"Missing Return Annotations:{result.missing_return_annotations}")
        print(f"Explicit 'Any' References:  {result.any_uses_count}")
        print(f"Status:                    [{result.status}]")

        return result


def run() -> TypingCheckResult:
    """Module entry point."""
    return TypingAnalyzer().run()


if __name__ == "__main__":
    run()
