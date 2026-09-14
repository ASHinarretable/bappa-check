from __future__ import annotations

from pathlib import Path

from bappa_check.checks import whitespace
from bappa_check.checks.base import Severity


def test_flags_trailing_whitespace(tmp_path: Path) -> None:
    path = tmp_path / "f.py"
    path.write_bytes(b"line one   \nline two\n")
    findings = whitespace.run([path])
    assert len(findings) == 1
    assert findings[0].severity == Severity.WARN
    assert findings[0].line == 1


def test_flags_missing_eof_newline(tmp_path: Path) -> None:
    path = tmp_path / "f.py"
    path.write_bytes(b"no newline at end")
    findings = whitespace.run([path])
    assert any("missing newline" in f.message for f in findings)


def test_clean_file_has_no_findings(tmp_path: Path) -> None:
    path = tmp_path / "f.py"
    path.write_bytes(b"clean line\nanother clean line\n")
    assert whitespace.run([path]) == []
