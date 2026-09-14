"""Trailing whitespace and missing end-of-file newline — cosmetic, warn only."""

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
            raw = path.read_bytes()
        except OSError:
            continue
        if not raw:
            continue

        text = raw.decode("utf-8", errors="replace")
        for lineno, line in enumerate(text.split("\n"), start=1):
            stripped_cr = line.rstrip("\r")
            if stripped_cr != stripped_cr.rstrip(" \t"):
                findings.append(
                    Finding(path=path, line=lineno, message="trailing whitespace", severity=Severity.WARN)
                )

        if not raw.endswith(b"\n"):
            findings.append(
                Finding(path=path, message="missing newline at end of file", severity=Severity.WARN)
            )
    return findings
