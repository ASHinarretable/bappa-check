from __future__ import annotations

from pathlib import Path

from bappa_check.checks import todo_fixme
from bappa_check.checks.base import Severity


def test_flags_todo_as_info_only(tmp_path: Path) -> None:
    path = tmp_path / "f.py"
    path.write_text("# TODO: refactor this\nprint(1)\n", encoding="utf-8")
    findings = todo_fixme.run([path])
    assert len(findings) == 1
    assert findings[0].severity == Severity.INFO


def test_flags_fixme_case_insensitive(tmp_path: Path) -> None:
    path = tmp_path / "f.py"
    path.write_text("# fixme: this is broken\n", encoding="utf-8")
    assert len(todo_fixme.run([path])) == 1


def test_clean_file_has_no_findings(tmp_path: Path) -> None:
    path = tmp_path / "f.py"
    path.write_text("print('done, no markers here')\n", encoding="utf-8")
    assert todo_fixme.run([path]) == []
