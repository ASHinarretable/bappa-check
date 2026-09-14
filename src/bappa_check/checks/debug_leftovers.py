"""Catch debugger breakpoints and stray console logging left in source.

Warns rather than fails — plenty of teams commit a `console.log` on purpose
in a WIP branch, and `--strict` exists for teams that want it to block.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from pathlib import Path

from bappa_check.checks.base import Finding, Severity
from bappa_check.git import is_binary

TEST_DIR_NAMES = {"test", "tests", "__tests__", "spec"}

PATTERNS = [
    re.compile(r"\bpdb\.set_trace\(\)"),
    re.compile(r"\bbreakpoint\(\)"),
    re.compile(r"\bdebugger\s*;"),
    re.compile(r"\bconsole\.log\("),
]


def _looks_like_test(path: Path) -> bool:
    # Match whole path components / filename patterns, not a raw substring —
    # a substring check would misfire on e.g. "latest_report.py" (contains
    # "test_") or any tmp directory that happens to have "test" in its name.
    if any(part.lower() in TEST_DIR_NAMES for part in path.parts[:-1]):
        return True
    name = path.name.lower()
    return name.startswith("test_") or name.endswith("_test.py") or ".test." in name or ".spec." in name


def run(files: Sequence[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for path in files:
        if not path.is_file() or is_binary(path) or _looks_like_test(path):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        for lineno, line in enumerate(text.splitlines(), start=1):
            for pattern in PATTERNS:
                if pattern.search(line):
                    findings.append(
                        Finding(
                            path=path,
                            line=lineno,
                            message=f"debug leftover: {line.strip()[:60]}",
                            severity=Severity.WARN,
                        )
                    )
                    break
    return findings
