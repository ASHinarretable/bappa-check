from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from bappa_check.checks import external


def test_returns_nothing_when_ruff_not_on_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(external.shutil, "which", lambda _name: None)
    path = tmp_path / "f.py"
    path.write_text("import os\n", encoding="utf-8")
    assert external.run([path]) == []


def test_parses_ruff_concise_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "f.py"
    path.write_text("import os\n", encoding="utf-8")

    monkeypatch.setattr(external.shutil, "which", lambda name: "/usr/bin/ruff" if name == "ruff" else None)

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args, returncode=1, stdout=f"{path}:1:1: F401 `os` imported but unused\n", stderr=""
        )

    monkeypatch.setattr(external.subprocess, "run", fake_run)

    findings = external.run([path])
    assert len(findings) == 1
    assert "F401" in findings[0].message


def test_survives_ruff_timeout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "f.py"
    path.write_text("import os\n", encoding="utf-8")
    monkeypatch.setattr(external.shutil, "which", lambda name: "/usr/bin/ruff" if name == "ruff" else None)

    def raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="ruff", timeout=30)

    monkeypatch.setattr(external.subprocess, "run", raise_timeout)
    assert external.run([path]) == []


def test_non_python_non_js_files_are_ignored(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(external.shutil, "which", lambda _name: "/usr/bin/ruff")
    path = tmp_path / "f.txt"
    path.write_text("hello\n", encoding="utf-8")
    assert external.run([path]) == []
