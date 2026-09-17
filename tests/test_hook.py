from __future__ import annotations

from pathlib import Path

from bappa_check import hook


def test_install_writes_hook_file(git_repo: Path) -> None:
    ok, message = hook.install(git_repo)
    assert ok is True
    hook_path = git_repo / ".git" / "hooks" / "pre-commit"
    assert hook_path.exists()
    assert hook.MARKER in hook_path.read_text(encoding="utf-8")
    assert "Installed" in message and str(hook_path) in message


def test_install_is_idempotent(git_repo: Path) -> None:
    hook.install(git_repo)
    ok, _ = hook.install(git_repo)
    assert ok is True


def test_install_refuses_to_clobber_foreign_hook(git_repo: Path) -> None:
    hook_path = git_repo / ".git" / "hooks" / "pre-commit"
    hook_path.parent.mkdir(parents=True, exist_ok=True)
    hook_path.write_text("#!/bin/sh\necho 'someone else was here'\n", encoding="utf-8")

    ok, message = hook.install(git_repo)
    assert ok is False
    assert "wasn't installed by bappa-check" in message
    # and it must not have touched the file
    assert "someone else was here" in hook_path.read_text(encoding="utf-8")


def test_install_fails_outside_a_git_repo(tmp_path: Path) -> None:
    ok, message = hook.install(tmp_path)
    assert ok is False
    assert "git repository" in message


def test_uninstall_removes_our_hook(git_repo: Path) -> None:
    hook.install(git_repo)
    ok, _ = hook.uninstall(git_repo)
    assert ok is True
    assert not (git_repo / ".git" / "hooks" / "pre-commit").exists()


def test_uninstall_refuses_foreign_hook(git_repo: Path) -> None:
    hook_path = git_repo / ".git" / "hooks" / "pre-commit"
    hook_path.parent.mkdir(parents=True, exist_ok=True)
    hook_path.write_text("#!/bin/sh\necho 'not ours'\n", encoding="utf-8")

    ok, message = hook.uninstall(git_repo)
    assert ok is False
    assert "wasn't installed by bappa-check" in message
    assert hook_path.exists()


def test_uninstall_when_nothing_installed(git_repo: Path) -> None:
    ok, message = hook.uninstall(git_repo)
    assert ok is False
    assert "No pre-commit hook" in message
