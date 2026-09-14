from __future__ import annotations

from pathlib import Path

from bappa_check.checks import overall_passed, run_all
from bappa_check.checks.base import CheckResult, Finding, Severity


def test_run_all_returns_one_result_per_registered_check(tmp_path: Path) -> None:
    path = tmp_path / "clean.py"
    path.write_text("print('hi')\n", encoding="utf-8")
    results = run_all([path])
    names = {r.name for r in results}
    assert names == {
        "conflict-markers",
        "secrets",
        "large-files",
        "syntax",
        "debug-leftovers",
        "whitespace",
        "todo-fixme",
        "external-lint",
    }


def test_clean_file_passes_everything(tmp_path: Path) -> None:
    path = tmp_path / "clean.py"
    path.write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    results = run_all([path])
    assert overall_passed(results)


def test_fail_finding_blocks_by_default() -> None:
    results = [CheckResult(name="x", findings=[Finding(path=Path("f"), message="bad", severity=Severity.FAIL)])]
    assert overall_passed(results) is False


def test_warn_finding_does_not_block_by_default() -> None:
    results = [CheckResult(name="x", findings=[Finding(path=Path("f"), message="meh", severity=Severity.WARN)])]
    assert overall_passed(results) is True


def test_warn_finding_blocks_in_strict_mode() -> None:
    results = [CheckResult(name="x", findings=[Finding(path=Path("f"), message="meh", severity=Severity.WARN)])]
    assert overall_passed(results, strict=True) is False


def test_info_finding_never_blocks() -> None:
    results = [CheckResult(name="x", findings=[Finding(path=Path("f"), message="fyi", severity=Severity.INFO)])]
    assert overall_passed(results, strict=True) is True
