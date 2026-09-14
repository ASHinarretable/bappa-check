from __future__ import annotations

from pathlib import Path

from bappa_check.checks import large_files
from bappa_check.checks.base import Severity


def test_flags_file_over_limit(tmp_path: Path) -> None:
    path = tmp_path / "big.bin"
    path.write_bytes(b"0" * 1024)
    findings = large_files.run([path], max_bytes=512)
    assert len(findings) == 1
    assert findings[0].severity == Severity.FAIL


def test_passes_file_under_limit(tmp_path: Path) -> None:
    path = tmp_path / "small.bin"
    path.write_bytes(b"0" * 100)
    assert large_files.run([path], max_bytes=512) == []


def test_default_limit_is_five_megabytes() -> None:
    assert large_files.DEFAULT_MAX_BYTES == 5 * 1024 * 1024
