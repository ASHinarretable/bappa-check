from __future__ import annotations

from pathlib import Path

from bappa_check.checks import conflict_markers
from bappa_check.checks.base import Severity


def test_flags_full_conflict_block(tmp_path: Path) -> None:
    path = tmp_path / "f.py"
    path.write_text(
        "<<<<<<< HEAD\nours\n=======\ntheirs\n>>>>>>> feature\n", encoding="utf-8"
    )
    findings = conflict_markers.run([path])
    assert len(findings) == 3
    assert all(f.severity == Severity.FAIL for f in findings)


def test_ignores_markdown_underline(tmp_path: Path) -> None:
    path = tmp_path / "README.md"
    path.write_text("Title\n=======\n\nSome text.\n", encoding="utf-8")
    assert conflict_markers.run([path]) == []


def test_clean_file_has_no_findings(tmp_path: Path) -> None:
    path = tmp_path / "f.py"
    path.write_text("print('hello')\n", encoding="utf-8")
    assert conflict_markers.run([path]) == []
