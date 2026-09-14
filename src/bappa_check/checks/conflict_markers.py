"""Detect unresolved merge-conflict markers left in a file.

Only flags a file when it contains BOTH a `<<<<<<<` start marker and a
`>>>>>>>` end marker — a lone `=======` (e.g. a Markdown h1 underline) is
never enough on its own, to avoid false positives on prose files.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from bappa_check.checks.base import Finding, Severity
from bappa_check.git import is_binary


def run(files: Sequence[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for path in files:
        if not path.is_file() or is_binary(path):
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue

        hits = [
            (lineno, line)
            for lineno, line in enumerate(lines, start=1)
            if line.startswith(("<<<<<<<", ">>>>>>>")) or line.rstrip() == "======="
        ]
        has_start = any(line.startswith("<<<<<<<") for _, line in hits)
        has_end = any(line.startswith(">>>>>>>") for _, line in hits)
        if not (has_start and has_end):
            continue

        for lineno, line in hits:
            findings.append(
                Finding(
                    path=path,
                    line=lineno,
                    message=f"unresolved merge-conflict marker: {line.strip()[:40]!r}",
                    severity=Severity.FAIL,
                )
            )
    return findings
