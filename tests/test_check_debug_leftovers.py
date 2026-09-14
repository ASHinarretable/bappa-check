from __future__ import annotations

from pathlib import Path

from bappa_check.checks import debug_leftovers
from bappa_check.checks.base import Severity


def test_flags_python_breakpoint(tmp_path: Path) -> None:
    path = tmp_path / "app.py"
    path.write_text("x = 1\nbreakpoint()\n", encoding="utf-8")
    findings = debug_leftovers.run([path])
    assert len(findings) == 1
    assert findings[0].severity == Severity.WARN


def test_flags_console_log(tmp_path: Path) -> None:
    path = tmp_path / "app.js"
    path.write_text("console.log('debug me');\n", encoding="utf-8")
    assert len(debug_leftovers.run([path])) == 1


def test_skips_test_files(tmp_path: Path) -> None:
    path = tmp_path / "test_app.py"
    path.write_text("breakpoint()\n", encoding="utf-8")
    assert debug_leftovers.run([path]) == []


def test_clean_file_has_no_findings(tmp_path: Path) -> None:
    path = tmp_path / "app.py"
    path.write_text("print('normal output')\n", encoding="utf-8")
    assert debug_leftovers.run([path]) == []
