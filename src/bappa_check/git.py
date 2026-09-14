"""Small git plumbing wrappers — no external git library needed."""

from __future__ import annotations

import subprocess
from pathlib import Path


def _git(*args: str, cwd: Path | None = None) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def repo_root(cwd: Path | None = None) -> Path | None:
    """Return the top level of the current git repo, or None if not in one."""
    try:
        out = _git("rev-parse", "--show-toplevel", cwd=cwd)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return Path(out.strip())


def staged_files(cwd: Path | None = None) -> list[Path]:
    """Files staged for commit (added, copied, modified, renamed)."""
    root = repo_root(cwd)
    if root is None:
        return []
    try:
        out = _git("diff", "--cached", "--name-only", "--diff-filter=ACMR", cwd=cwd)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [root / line for line in out.splitlines() if line.strip()]


def all_tracked_files(cwd: Path | None = None) -> list[Path]:
    root = repo_root(cwd)
    if root is None:
        return []
    try:
        out = _git("ls-files", cwd=cwd)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [root / line for line in out.splitlines() if line.strip()]


def is_binary(path: Path) -> bool:
    """Cheap binary sniff: a NUL byte in the first chunk means "don't treat as text"."""
    try:
        with open(path, "rb") as handle:
            chunk = handle.read(8192)
    except OSError:
        return True
    return b"\x00" in chunk
