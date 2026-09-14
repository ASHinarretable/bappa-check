"""Basic syntax validation for a handful of common file types.

Kept deliberately dependency-light: Python via `ast`, JSON via the stdlib,
TOML via `tomllib` when available (3.11+), YAML only if PyYAML happens to be
installed (the `yaml` extra). Anything else is skipped, not failed.
"""

from __future__ import annotations

import ast
import json
from collections.abc import Sequence
from pathlib import Path

from bappa_check.checks.base import Finding, Severity


def _check_python(path: Path, text: str) -> Finding | None:
    try:
        ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        return Finding(path=path, line=exc.lineno, message=f"SyntaxError: {exc.msg}", severity=Severity.FAIL)
    return None


def _check_json(path: Path, text: str) -> Finding | None:
    try:
        json.loads(text)
    except json.JSONDecodeError as exc:
        return Finding(path=path, line=exc.lineno, message=f"invalid JSON: {exc.msg}", severity=Severity.FAIL)
    return None


def _check_toml(path: Path, text: str) -> Finding | None:
    try:
        import tomllib
    except ImportError:
        return None  # no bundled TOML parser before Python 3.11 — skip, don't fail
    try:
        tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        return Finding(path=path, message=f"invalid TOML: {exc}", severity=Severity.FAIL)
    return None


def _check_yaml(path: Path, text: str) -> Finding | None:
    try:
        import yaml
    except ImportError:
        return None  # optional extra not installed — skip, don't fail
    try:
        list(yaml.safe_load_all(text))
    except yaml.YAMLError as exc:
        return Finding(path=path, message=f"invalid YAML: {exc}", severity=Severity.FAIL)
    return None


CHECKERS = {
    ".py": _check_python,
    ".json": _check_json,
    ".toml": _check_toml,
    ".yml": _check_yaml,
    ".yaml": _check_yaml,
}


def run(files: Sequence[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for path in files:
        if not path.is_file():
            continue
        checker = CHECKERS.get(path.suffix.lower())
        if checker is None:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            findings.append(Finding(path=path, message=f"could not read file: {exc}", severity=Severity.FAIL))
            continue
        finding = checker(path, text)
        if finding is not None:
            findings.append(finding)
    return findings
