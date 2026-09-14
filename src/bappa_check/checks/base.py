"""Shared types for all checks."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable


class Severity(Enum):
    INFO = "info"
    WARN = "warn"
    FAIL = "fail"


_ORDER = {Severity.INFO: 0, Severity.WARN: 1, Severity.FAIL: 2}


def worse(a: Severity, b: Severity) -> Severity:
    return a if _ORDER[a] >= _ORDER[b] else b


@dataclass
class Finding:
    path: Path
    message: str
    line: int | None = None
    severity: Severity = Severity.FAIL

    def format(self) -> str:
        loc = f"{self.path}:{self.line}" if self.line is not None else str(self.path)
        return f"{loc}  {self.message}"


# A check is any callable that takes the candidate files and returns findings.
CheckFn = Callable[[Sequence[Path]], list[Finding]]


@dataclass
class Check:
    name: str
    run: CheckFn
    description: str = ""


@dataclass
class CheckResult:
    name: str
    findings: list[Finding] = field(default_factory=list)

    @property
    def severity(self) -> Severity:
        result = Severity.INFO
        for finding in self.findings:
            result = worse(result, finding.severity)
        return result

    @property
    def passed(self) -> bool:
        return self.severity != Severity.FAIL
