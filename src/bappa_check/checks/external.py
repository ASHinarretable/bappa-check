"""Optional passthrough to linters already on the user's machine.

Never required, never installed by us, and never crashes the run: if
`ruff`/`eslint` aren't on PATH (or misbehave), this check simply reports
nothing.
"""

from __future__ import annotations

import shutil
import subprocess
from collections.abc import Sequence
from pathlib import Path

from bappa_check.checks.base import Finding, Severity
from bappa_check.git import repo_root

TIMEOUT_SECONDS = 30


def _run_ruff(py_files: list[Path]) -> list[Finding]:
    ruff = shutil.which("ruff")
    if not ruff or not py_files:
        return []
    try:
        result = subprocess.run(
            [ruff, "check", "--output-format=concise", *[str(p) for p in py_files]],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            check=False,  # ruff exits non-zero when it finds issues — that's expected, not an error
        )
    except (OSError, subprocess.TimeoutExpired):
        return []

    findings: list[Finding] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        path_part = line.split(":", 1)[0]
        findings.append(Finding(path=Path(path_part), message=f"ruff: {line}", severity=Severity.WARN))
    return findings


def _run_eslint(js_files: list[Path], root: Path | None) -> list[Finding]:
    eslint = shutil.which("eslint")
    if not eslint or not js_files or root is None or not (root / "package.json").exists():
        return []
    try:
        result = subprocess.run(
            [eslint, "--format=compact", *[str(p) for p in js_files]],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            cwd=root,
            check=False,  # eslint exits non-zero when it finds issues — that's expected, not an error
        )
    except (OSError, subprocess.TimeoutExpired):
        return []

    findings: list[Finding] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line or line.endswith("problems"):
            continue
        path_part = line.split(":", 1)[0]
        findings.append(Finding(path=Path(path_part), message=f"eslint: {line}", severity=Severity.WARN))
    return findings


def run(files: Sequence[Path]) -> list[Finding]:
    py_files = [p for p in files if p.is_file() and p.suffix == ".py"]
    js_files = [p for p in files if p.is_file() and p.suffix in {".js", ".jsx", ".ts", ".tsx"}]
    findings = _run_ruff(py_files)
    if js_files:
        # Only shell out to `git rev-parse` (to find package.json) when there's
        # actually JS/TS staged — no point paying that cost otherwise.
        findings += _run_eslint(js_files, repo_root())
    return findings
