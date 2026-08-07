"""
Main entry point for the EvoPharm Architecture Analyzer.
"""

from __future__ import annotations

import sys
import traceback

from architecture_report import ArchitectureReport


ANALYZERS = (
    ("Domain", "analyze_domain"),
    ("Architecture", "analyze_architecture"),
    ("Dependencies", "analyze_dependencies"),
    ("Typing", "analyze_typing"),
    ("Tests", "analyze_tests"),
)


def run_analyzer(name: str, module_name: str) -> bool:
    """
    Import and execute an analyzer.
    """

    print(f"\n▶ Running {name} Analyzer")

    try:
        module = __import__(module_name)

        if not hasattr(module, "run"):
            print(f"❌ {module_name}.py does not define run()")
            return False

        module.run()

        print(f"✅ {name} completed")
        return True

    except Exception:
        print(f"❌ {name} failed")
        traceback.print_exc()
        return False


def main() -> int:

    ArchitectureReport.title("EVOPHARM ARCHITECTURE ANALYZER")

    success = True

    for name, module in ANALYZERS:
        ok = run_analyzer(name, module)
        success &= ok

    print()

    if success:
        print("✔ Analysis completed successfully.")
        return 0

    print("✘ Analysis finished with errors.")
    return 1


if __name__ == "__main__":
    sys.exit(main())