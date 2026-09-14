from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """A real, empty git repo in a tmp dir, with a usable local identity."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "bappa@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Bappa Test"], cwd=tmp_path, check=True)
    return tmp_path


def write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return path


def stage(repo: Path, *relative_paths: str) -> None:
    subprocess.run(["git", "add", *relative_paths], cwd=repo, check=True)
