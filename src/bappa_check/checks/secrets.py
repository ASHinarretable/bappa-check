"""Look for obviously-hardcoded credentials in staged text files.

This is a fast regex sweep, not a substitute for a real secret scanner
(gitleaks / trufflehog). It catches the "oops, committed my key" case.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from pathlib import Path

from bappa_check.checks.base import Finding, Severity
from bappa_check.git import is_binary

# Files that legitimately contain fake/example secrets.
SKIP_SUFFIXES = {".md", ".example", ".sample", ".lock"}
SKIP_NAMES = {".env.example", ".env.sample"}

# Inline escape hatch: `password = "..."  # bappa: ignore`
IGNORE_MARKER = "bappa: ignore"

PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("AWS access key ID", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("AWS secret access key", re.compile(r"(?i)aws_secret_access_key\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{40}")),
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("Slack token", re.compile(r"xox[abp]-[A-Za-z0-9-]{10,}")),
    (
        "hardcoded secret assignment",
        re.compile(r"(?i)\b(api[_-]?key|secret|password|token)\b\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
    ),
]


def _should_skip(path: Path) -> bool:
    return path.suffix.lower() in SKIP_SUFFIXES or path.name in SKIP_NAMES


def run(files: Sequence[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for path in files:
        if not path.is_file() or is_binary(path) or _should_skip(path):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        for lineno, line in enumerate(text.splitlines(), start=1):
            if IGNORE_MARKER in line:
                continue
            for label, pattern in PATTERNS:
                if pattern.search(line):
                    findings.append(
                        Finding(
                            path=path,
                            line=lineno,
                            message=f"possible secret ({label})",
                            severity=Severity.FAIL,
                        )
                    )
                    break  # one finding per line is enough
    return findings
