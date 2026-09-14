from __future__ import annotations

import sys
from pathlib import Path

import pytest

from bappa_check.checks import syntax
from bappa_check.checks.base import Severity


def test_flags_invalid_python(tmp_path: Path) -> None:
    path = tmp_path / "bad.py"
    path.write_text("def broken(:\n    pass\n", encoding="utf-8")
    findings = syntax.run([path])
    assert len(findings) == 1
    assert findings[0].severity == Severity.FAIL


def test_valid_python_passes(tmp_path: Path) -> None:
    path = tmp_path / "good.py"
    path.write_text("def ok():\n    return 1\n", encoding="utf-8")
    assert syntax.run([path]) == []


def test_flags_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text('{"a": 1,}\n', encoding="utf-8")
    assert len(syntax.run([path])) == 1


def test_valid_json_passes(tmp_path: Path) -> None:
    path = tmp_path / "good.json"
    path.write_text('{"a": 1}\n', encoding="utf-8")
    assert syntax.run([path]) == []


@pytest.mark.skipif(sys.version_info < (3, 11), reason="tomllib needs Python 3.11+")
def test_flags_invalid_toml(tmp_path: Path) -> None:
    path = tmp_path / "bad.toml"
    path.write_text("a = [1, 2\n", encoding="utf-8")
    assert len(syntax.run([path])) == 1


def test_unknown_extension_is_skipped(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("anything goes here (((\n", encoding="utf-8")
    assert syntax.run([path]) == []
