from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
from conftest import stage, write

from bappa_check import cli


def run_cli(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "bappa_check", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def test_version_flag() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "bappa_check", "--version"], capture_output=True, text=True, timeout=30, check=False
    )
    assert result.returncode == 0
    assert "bappa-check" in result.stdout


def test_nothing_staged_exits_zero(git_repo: Path) -> None:
    result = run_cli(git_repo)
    assert result.returncode == 0
    assert "Nothing staged" in result.stdout


def test_clean_staged_file_passes(git_repo: Path) -> None:
    write(git_repo / "app.py", "def add(a, b):\n    return a + b\n")
    stage(git_repo, "app.py")
    result = run_cli(git_repo)
    assert result.returncode == 0
    assert "BAPPA APPROVED" in result.stdout


def test_secret_in_staged_file_blocks_commit(git_repo: Path) -> None:
    write(git_repo / "config.py", 'AWS_KEY = "AKIAABCDEFGHIJKLMNOP"\n')
    stage(git_repo, "config.py")
    result = run_cli(git_repo)
    assert result.returncode == 1
    assert "BAPPA SAYS: NOT YET" in result.stdout
    assert "possible secret" in result.stdout


def test_warn_only_passes_without_strict(git_repo: Path) -> None:
    write(git_repo / "app.py", "x = 1\nbreakpoint()\n")
    stage(git_repo, "app.py")
    result = run_cli(git_repo)
    assert result.returncode == 0
    assert "BAPPA APPROVED" in result.stdout


def test_warn_blocks_with_strict(git_repo: Path) -> None:
    write(git_repo / "app.py", "x = 1\nbreakpoint()\n")
    stage(git_repo, "app.py")
    result = run_cli(git_repo, "--strict")
    assert result.returncode == 1
    assert "BAPPA SAYS: NOT YET" in result.stdout


def test_explicit_path_args_bypass_git_staging(git_repo: Path) -> None:
    # Not staged at all -- but passed explicitly, the way pre-commit calls hooks.
    write(git_repo / "config.py", 'AWS_KEY = "AKIAABCDEFGHIJKLMNOP"\n')
    result = run_cli(git_repo, "config.py")
    assert result.returncode == 1
    assert "possible secret" in result.stdout


def test_all_flag_checks_committed_files(git_repo: Path) -> None:
    write(git_repo / "config.py", 'AWS_KEY = "AKIAABCDEFGHIJKLMNOP"\n')
    stage(git_repo, "config.py")
    subprocess.run(["git", "commit", "-q", "-m", "add config"], cwd=git_repo, check=True)
    result = run_cli(git_repo, "--all")
    assert result.returncode == 1
    assert "possible secret" in result.stdout


def test_outside_git_repo_with_no_paths_exits_zero(tmp_path: Path) -> None:
    # Cap git's upward search at the system temp root, in case a parent
    # directory (e.g. $HOME) happens to be a repo on this machine.
    env = {**os.environ, "GIT_CEILING_DIRECTORIES": tempfile.gettempdir()}
    result = subprocess.run(
        [sys.executable, "-m", "bappa_check"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
        env=env,
    )
    assert result.returncode == 0
    assert "Not inside a git repository" in result.stdout


def test_install_and_uninstall_hook_via_cli(git_repo: Path) -> None:
    install_result = run_cli(git_repo, "--install-hook")
    assert install_result.returncode == 0
    assert (git_repo / ".git" / "hooks" / "pre-commit").exists()

    uninstall_result = run_cli(git_repo, "--uninstall-hook")
    assert uninstall_result.returncode == 0
    assert not (git_repo / ".git" / "hooks" / "pre-commit").exists()


# --- _make_console: trust a real TTY over Rich's own (sometimes overly
# conservative) auto-detection, and force color under pre-commit/CI too. ---


class _FakeStdout:
    def __init__(self, is_tty: bool) -> None:
        self._is_tty = is_tty

    def isatty(self) -> bool:
        return self._is_tty


def _clear_ci_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv("PRE_COMMIT", raising=False)


def test_make_console_forces_terminal_on_a_real_tty(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_ci_env(monkeypatch)
    monkeypatch.setattr(cli.sys, "stdout", _FakeStdout(True))
    console = cli._make_console()
    assert console.is_terminal is True


def test_make_console_leaves_autodetect_alone_on_a_plain_pipe(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_ci_env(monkeypatch)
    monkeypatch.setattr(cli.sys, "stdout", _FakeStdout(False))
    console = cli._make_console()
    # Not forced -- Rich's normal auto-detect applies, which for a non-tty
    # fake stream correctly reports not-a-terminal.
    assert console.is_terminal is False


def test_make_console_forces_terminal_under_ci_env(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_ci_env(monkeypatch)
    monkeypatch.setattr(cli.sys, "stdout", _FakeStdout(False))
    monkeypatch.setenv("CI", "true")
    console = cli._make_console()
    assert console.is_terminal is True


def test_make_console_forces_terminal_under_pre_commit_env(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_ci_env(monkeypatch)
    monkeypatch.setattr(cli.sys, "stdout", _FakeStdout(False))
    monkeypatch.setenv("PRE_COMMIT", "1")
    console = cli._make_console()
    assert console.is_terminal is True


def test_make_console_handles_a_stdout_without_isatty(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_ci_env(monkeypatch)

    class NoIsatty:
        pass

    monkeypatch.setattr(cli.sys, "stdout", NoIsatty())
    console = cli._make_console()  # must not raise
    assert console.is_terminal is False
