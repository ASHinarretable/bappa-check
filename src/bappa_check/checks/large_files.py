"""Flag files that are too large to belong in git history."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from bappa_check.checks.base import Finding, Severity

DEFAULT_MAX_BYTES = 5 * 1024 * 1024  # 5 MB


def run(files: Sequence[Path], max_bytes: int = DEFAULT_MAX_BYTES) -> list[Finding]:
    findings: list[Finding] = []
    for path in files:
        if not path.is_file():
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size > max_bytes:
            findings.append(
                Finding(
                    path=path,
                    message=f"file is {size / 1_048_576:.1f} MB (limit {max_bytes / 1_048_576:.0f} MB)",
                    severity=Severity.FAIL,
                )
            )
    return findings
