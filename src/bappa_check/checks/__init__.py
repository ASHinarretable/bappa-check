"""Check registry and orchestration."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from bappa_check.checks import (
    conflict_markers,
    debug_leftovers,
    external,
    large_files,
    secrets,
    syntax,
    todo_fixme,
    whitespace,
)
from bappa_check.checks.base import Check, CheckResult, Finding, Severity

REGISTRY: list[Check] = [
    Check("conflict-markers", conflict_markers.run, "Unresolved merge-conflict markers"),
    Check("secrets", secrets.run, "Hardcoded credentials / API keys"),
    Check("large-files", large_files.run, "Files staged that are too large"),
    Check("syntax", syntax.run, "Basic syntax validation (py / json / toml / yaml)"),
    Check("debug-leftovers", debug_leftovers.run, "Debugger breakpoints / console.log left in code"),
    Check("whitespace", whitespace.run, "Trailing whitespace / missing EOF newline"),
    Check("todo-fixme", todo_fixme.run, "TODO / FIXME markers (informational only)"),
    Check("external-lint", external.run, "ruff / eslint passthrough, only if already installed"),
]


def run_all(files: Sequence[Path]) -> list[CheckResult]:
    """Run every registered check against `files` and collect the results."""
    return [CheckResult(name=check.name, findings=check.run(files)) for check in REGISTRY]


def overall_passed(results: Sequence[CheckResult], strict: bool = False) -> bool:
    """A run passes if nothing FAILed, and (in --strict mode) nothing WARNed either."""
    for result in results:
        if result.severity == Severity.FAIL:
            return False
        if strict and result.severity == Severity.WARN:
            return False
    return True


__all__ = [
    "REGISTRY",
    "Check",
    "CheckResult",
    "Finding",
    "Severity",
    "overall_passed",
    "run_all",
]
