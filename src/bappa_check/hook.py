"""Install/uninstall bappa-check as a repo's native `.git/hooks/pre-commit`.

This is the "just works" path for someone who doesn't want the `pre-commit`
framework — one flag, one file. It never clobbers a hook it didn't write.
"""

from __future__ import annotations

import stat
from pathlib import Path

MARKER = "# installed by bappa-check"

HOOK_SCRIPT = f"""#!/bin/sh
{MARKER} -- https://github.com/ASHinarretable/bappa-check
exec bappa-check
"""


def _hook_path(repo_root: Path) -> Path:
    return repo_root / ".git" / "hooks" / "pre-commit"


def install(repo_root: Path) -> tuple[bool, str]:
    hooks_dir = repo_root / ".git" / "hooks"
    if not hooks_dir.is_dir():
        return False, f"{hooks_dir} not found -- is this a git repository?"

    hook_path = _hook_path(repo_root)
    if hook_path.exists():
        existing = hook_path.read_text(encoding="utf-8", errors="replace")
        if MARKER not in existing:
            return False, (
                f"{hook_path} already exists and wasn't installed by bappa-check.\n"
                f"Refusing to overwrite it -- add a line running `bappa-check` to it "
                f"yourself, or remove it first."
            )

    # Path.write_text()'s `newline` kwarg needs Python 3.10+; open() has always had it.
    with open(hook_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(HOOK_SCRIPT)
    try:
        mode = hook_path.stat().st_mode
        hook_path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except OSError:
        pass  # best-effort; irrelevant on Windows, required on POSIX
    return True, f"Installed pre-commit hook at {hook_path}"


def uninstall(repo_root: Path) -> tuple[bool, str]:
    hook_path = _hook_path(repo_root)
    if not hook_path.exists():
        return False, "No pre-commit hook is installed."

    existing = hook_path.read_text(encoding="utf-8", errors="replace")
    if MARKER not in existing:
        return False, (
            f"{hook_path} exists but wasn't installed by bappa-check.\n"
            f"Refusing to remove it -- delete it yourself if you're sure."
        )

    hook_path.unlink()
    return True, f"Removed pre-commit hook at {hook_path}"
