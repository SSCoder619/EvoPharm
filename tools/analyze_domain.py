"""
Domain analysis for the EvoPharm Architecture Analyzer.

Inspects bounded contexts, verifies expected file structure, counts DDD
building blocks, and computes a domain maturity score.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from config import (
    BOUNDED_CONTEXTS,
    DOMAIN_DIR,
    EXPECTED_DOMAIN_FILES,
    OPTIONAL_DOMAIN_FILES,
)
from common import (
    iter_subdirectories,
    plural,
    print_header,
    print_section,
)
from parser import FileInfo, PythonParser


@dataclass
class ContextMetrics:
    """Aggregated metrics for a single bounded context."""

    name: str
    path: Path
    required_files_present: int = 0
    optional_files_present: int = 0
    entities: int = 0
    aggregate_roots: int = 0
    value_objects: int = 0
    enums: int = 0
    exceptions: int = 0
    protocols: int = 0
    domain_services: int = 0
    specifications: int = 0
    domain_events: int = 0
    missing_files: list[str] = field(default_factory=list)


class DomainAnalyzer:
    """Analyzes the domain layer for DDD compliance and structural integrity."""

    def __init__(self) -> None:
        self.parser = PythonParser()
        self.contexts: list[ContextMetrics] = []

    def run(self) -> None:
        """Execute the domain analysis and print the comprehensive report."""
        print_header("Domain Analysis")
        self._discover_contexts()
        self._print_details()
        self._print_summary()

    def _discover_contexts(self) -> None:
        """Scan the domain directory for bounded contexts and analyze them."""
        if not DOMAIN_DIR.is_dir():
            print(f"⚠ Domain directory missing: {DOMAIN_DIR}")
            return

        discovered = {d.name for d in iter_subdirectories(DOMAIN_DIR)}
        target_contexts = (
            sorted(discovered & BOUNDED_CONTEXTS)
            if BOUNDED_CONTEXTS
            else sorted(discovered)
        )

        for ctx_name in target_contexts:
            ctx_path = DOMAIN_DIR / ctx_name
            self.contexts.append(self._analyze_context(ctx_name, ctx_path))

    def _analyze_context(self, name: str, path: Path) -> ContextMetrics:
        """Verify file structure and extract DDD primitive counts for a context."""
        metrics = ContextMetrics(name=name, path=path)

        for fname in EXPECTED_DOMAIN_FILES:
            fpath = path / fname
            if fpath.is_file():
                metrics.required_files_present += 1
                self._extract_primitives(fpath, metrics)
            else:
                metrics.missing_files.append(fname)

        for fname in OPTIONAL_DOMAIN_FILES:
            fpath = path / fname
            if fpath.is_file():
                metrics.optional_files_present += 1
                self._extract_primitives(fpath, metrics)

        return metrics

    def _extract_primitives(self, fpath: Path, metrics: ContextMetrics) -> None:
        """Parse a file and update context metrics based on its AST contents."""
        info = self.parser.parse(fpath)
        fname = fpath.name

        match fname:
            case "entities.py":
                # Dataclasses typically model regular entities with immutable or 
                # simple state. Plain classes often represent Aggregate Roots that 
                # manage lifecycle, invariants, and repository dependencies.
                metrics.entities += len(info.dataclasses)
                ar_candidates = [c for c in info.classes if c not in info.dataclasses]
                metrics.aggregate_roots += len(ar_candidates)

            case "value_objects.py":
                metrics.value_objects += len(info.dataclasses)

            case "enums.py":
                metrics.enums += len(info.enums)

            case "exceptions.py":
                metrics.exceptions += len(info.exceptions)

            case "interfaces.py":
                metrics.protocols += len(info.protocols)

            case "services.py":
                # Domain services can be implemented as classes or module-level functions
                metrics.domain_services += len(info.classes) + len(info.functions)

            case "specifications.py":
                metrics.specifications += len(info.classes)

            case "domain_events.py":
                metrics.domain_events += len(info.dataclasses) + len(info.classes)

    def _print_details(self) -> None:
        """Print detailed metrics for each discovered bounded context."""
        if not self.contexts:
            print("No bounded contexts found to analyze.")
            return

        for ctx in self.contexts:
            print_section(f"Context: {ctx.name}")
            status = "✔" if not ctx.missing_files else "⚠"
            print(f"{status} Required files: {ctx.required_files_present}/{len(EXPECTED_DOMAIN_FILES)}")
            print(f"  Optional files: {ctx.optional_files_present}/{len(OPTIONAL_DOMAIN_FILES)}")

            if ctx.missing_files:
                print(f"  Missing: {', '.join(sorted(ctx.missing_files))}")

            print(f"\n{plural(ctx.entities, 'Entity')}")
            print(f"{plural(ctx.aggregate_roots, 'Aggregate Root')}")
            print(f"{plural(ctx.value_objects, 'Value Object')}")
            print(f"{plural(ctx.enums, 'Enum')}")
            print(f"{plural(ctx.exceptions, 'Exception')}")
            print(f"{plural(ctx.protocols, 'Protocol')}")
            print(f"{plural(ctx.domain_services, 'Domain Service')}")
            print(f"{plural(ctx.specifications, 'Specification')}")
            print(f"{plural(ctx.domain_events, 'Domain Event')}\n")

    def _print_summary(self) -> None:
        """Calculate and print the overall domain maturity score."""
        if not self.contexts:
            return

        total_required = len(EXPECTED_DOMAIN_FILES) * len(self.contexts)
        total_optional = len(OPTIONAL_DOMAIN_FILES) * len(self.contexts)

        found_req = sum(c.required_files_present for c in self.contexts)
        found_opt = sum(c.optional_files_present for c in self.contexts)

        req_coverage = (found_req / total_required * 100) if total_required > 0 else 0.0
        opt_coverage = (found_opt / total_optional * 100) if total_optional > 0 else 0.0

        # DDD Maturity Score calculation:
        # 60% weight on required structure completeness
        # 20% weight on optional pattern adoption
        # 20% weight on domain primitive richness (capped at 100)
        primitives_total = sum(
            c.entities + c.aggregate_roots + c.value_objects + 
            c.enums + c.protocols for c in self.contexts
        )
        richness_factor = min(100.0, primitives_total * 2.5)

        ddd_score = (req_coverage * 0.6) + (opt_coverage * 0.2) + (richness_factor * 0.2)

        print_section("Domain Summary")
        print(f"Bounded Contexts Analyzed: {len(self.contexts)}")
        print(f"Required Structure Coverage: {req_coverage:.1f}%")
        print(f"Optional Pattern Coverage:   {opt_coverage:.1f}%")
        print(f"DDD Maturity Score:          {ddd_score:.1f}%")


def run() -> None:
    """Module entry point executed by the main analyzer runner."""
    DomainAnalyzer().run()