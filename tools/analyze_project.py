"""Legacy project-wide analyzer runner for EvoPharm Retail ERP."""

from __future__ import annotations

import sys
import traceback

try:
    from architecture_report import ArchitectureReport
except ImportError:
    from .architecture_report import ArchitectureReport


ANALYZERS = (
    ("Domain", "analyze_domain"),
    ("Application", "analyze_application"),
    ("Infrastructure", "analyze_infrastructure"),
    ("Architecture", "analyze_architecture"),
    ("Dependencies", "analyze_dependencies"),
    ("Typing", "analyze_typing"),
    ("Tests", "analyze_tests"),
)


def run_analyzer(name: str, module_name: str) -> bool:
    """Import and execute an analyzer."""
    print(f"\n[RUN] Running {name} Analyzer")

    try:
        if module_name in sys.modules:
            module = sys.modules[module_name]
        else:
            module = __import__(module_name)

        if not hasattr(module, "run"):
            print(f"[FAIL] {module_name}.py does not define run()")
            return False

        module.run()

        print(f"[PASS] {name} completed")
        return True

    except Exception:
        print(f"[FAIL] {name} failed")
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
        print("[PASS] Analysis completed successfully.")
        return 0

    print("[FAIL] Analysis finished with errors.")
    return 1


if __name__ == "__main__":
    sys.exit(main())