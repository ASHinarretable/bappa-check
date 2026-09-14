from __future__ import annotations

from pathlib import Path

from bappa_check.checks import secrets
from bappa_check.checks.base import Severity


def test_flags_aws_access_key(tmp_path: Path) -> None:
    path = tmp_path / "config.py"
    path.write_text('AWS_KEY = "AKIAABCDEFGHIJKLMNOP"\n', encoding="utf-8")
    findings = secrets.run([path])
    assert len(findings) == 1
    assert findings[0].severity == Severity.FAIL


def test_flags_private_key_block(tmp_path: Path) -> None:
    path = tmp_path / "id_rsa"
    path.write_text("-----BEGIN RSA PRIVATE KEY-----\nMIIB...\n", encoding="utf-8")
    assert len(secrets.run([path])) == 1


def test_flags_generic_password_assignment(tmp_path: Path) -> None:
    path = tmp_path / "settings.py"
    path.write_text('password = "hunter2ButLonger"\n', encoding="utf-8")
    assert len(secrets.run([path])) == 1


def test_ignore_marker_suppresses_finding(tmp_path: Path) -> None:
    path = tmp_path / "settings.py"
    path.write_text('password = "hunter2ButLonger"  # bappa: ignore\n', encoding="utf-8")
    assert secrets.run([path]) == []


def test_skips_markdown_and_example_files(tmp_path: Path) -> None:
    md = tmp_path / "README.md"
    md.write_text('AWS_KEY = "AKIAABCDEFGHIJKLMNOP"\n', encoding="utf-8")
    example = tmp_path / "settings.py.example"
    example.write_text('password = "hunter2ButLonger"\n', encoding="utf-8")
    assert secrets.run([md, example]) == []


def test_clean_file_has_no_findings(tmp_path: Path) -> None:
    path = tmp_path / "app.py"
    path.write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    assert secrets.run([path]) == []
