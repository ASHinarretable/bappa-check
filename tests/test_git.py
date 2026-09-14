from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from conftest import stage, write

from bappa_check.git import all_tracked_files, is_binary, repo_root, staged_files


def test_repo_root_finds_toplevel(git_repo: Path) -> None:
    assert repo_root(git_repo) == git_repo


def test_repo_root_none_outside_git(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # tmp_path has no .git of its own, but git walks *up* looking for one — on
    # a machine where a parent directory (e.g. $HOME) happens to be a repo,
    # that would leak through. Cap the search at the system temp root so this
    # test reflects "not in a repo" regardless of the host's own setup.
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", tempfile.gettempdir())
    assert repo_root(tmp_path) is None


def test_staged_files_lists_added_file(git_repo: Path) -> None:
    write(git_repo / "a.txt", "hello\n")
    stage(git_repo, "a.txt")
    assert staged_files(git_repo) == [git_repo / "a.txt"]


def test_staged_files_empty_when_nothing_staged(git_repo: Path) -> None:
    write(git_repo / "untracked.txt", "hello\n")
    assert staged_files(git_repo) == []


def test_all_tracked_files_needs_a_commit(git_repo: Path) -> None:
    write(git_repo / "a.txt", "hello\n")
    stage(git_repo, "a.txt")
    # staged-but-uncommitted files ARE listed by `git ls-files`.
    assert git_repo / "a.txt" in all_tracked_files(git_repo)


def test_is_binary_detects_null_byte(tmp_path: Path) -> None:
    binary = tmp_path / "bin.dat"
    binary.write_bytes(b"\x00\x01\x02")
    assert is_binary(binary) is True


def test_is_binary_false_for_text(tmp_path: Path) -> None:
    text = write(tmp_path / "plain.txt", "just text\n")
    assert is_binary(text) is False


def test_is_binary_true_for_missing_file(tmp_path: Path) -> None:
    assert is_binary(tmp_path / "does-not-exist.txt") is True
