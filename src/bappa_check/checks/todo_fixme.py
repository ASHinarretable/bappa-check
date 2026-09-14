"""Report TODO/FIXME markers. Purely informational — never blocks a commit."""

from __future__ import annotations

import re
from collections.abc import Sequence
from pathlib import Path

from bappa_check.checks.base import Finding, Severity
from bappa_check.git import is_binary

PATTERN = re.compile(r"\b(TODO|FIXME)\b", re.IGNORECASE)


def run(files: Sequence[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for path in files:
        if not path.is_file() or is_binary(path):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        for lineno, line in enumerate(text.splitlines(), start=1):
            if PATTERN.search(line):
                findings.append(
                    Finding(path=path, line=lineno, message=line.strip()[:80], severity=Severity.INFO)
                )
    return findings
