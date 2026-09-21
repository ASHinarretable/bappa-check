"""bappa-check command-line entry point."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from bappa_check import __version__, animate, art, git, hook
from bappa_check.checks import CheckResult, Severity, overall_passed, run_all

_STATUS_LABEL = {Severity.INFO: "info", Severity.WARN: "WARN", Severity.FAIL: "FAIL"}
_STATUS_STYLE = {Severity.INFO: "cyan", Severity.WARN: "yellow", Severity.FAIL: "red"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bappa-check",
        description="Sanity-check your staged files before you commit.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        metavar="PATH",
        help="specific files/directories to check (default: staged files)",
    )
    parser.add_argument("--all", action="store_true", help="check every tracked file, not just staged ones")
    parser.add_argument("--strict", action="store_true", help="treat WARN findings as failures")
    parser.add_argument("--no-anim", action="store_true", help="skip the animation, print static art only")
    parser.add_argument(
        "--install-hook", action="store_true", help="install bappa-check as this repo's git pre-commit hook"
    )
    parser.add_argument("--uninstall-hook", action="store_true", help="remove the bappa-check pre-commit hook")
    parser.add_argument("--version", action="version", version=f"bappa-check {__version__}")
    return parser


def _expand_path(raw: str) -> list[Path]:
    path = Path(raw)
    if path.is_dir():
        return [f for f in path.rglob("*") if f.is_file()]
    return [path]


def _resolve_files(args: argparse.Namespace) -> list[Path] | None:
    """Files to check, or None if we're not in a git repo and no paths were given."""
    if args.paths:
        files: list[Path] = []
        for raw in args.paths:
            files.extend(_expand_path(raw))
        return files

    root = git.repo_root()
    if root is None:
        return None
    return git.all_tracked_files() if args.all else git.staged_files()


def _print_checklist(console: Console, results: list[CheckResult]) -> None:
    table = Table(show_header=True, header_style="bold")
    table.add_column("check")
    table.add_column("status")
    table.add_column("findings")

    for result in results:
        count = len(result.findings)
        if count == 0:
            status = "[green]ok[/green]"
        else:
            label = _STATUS_LABEL[result.severity]
            style = _STATUS_STYLE[result.severity]
            status = f"[{style}]{label}[/{style}]"
        summary = f"{count} finding{'s' if count != 1 else ''}" if count else "-"
        table.add_row(result.name, status, summary)

    console.print(table)

    for result in results:
        if not result.findings:
            continue
        console.print(f"\n[bold]{result.name}[/bold]")
        for finding in result.findings:
            console.print(f"  {finding.format()}")


def _make_console() -> Console:
    """Build the Console bappa-check prints through.

    Rich's own auto-detection (`Console()` with no arguments) can be overly
    conservative about what counts as a color-capable terminal -- observed
    directly: a real interactive session with TERM=xterm-256color still had
    Rich report color_system=None. If stdout genuinely is a TTY, trust that
    over Rich's heuristics and force color on (Rich still separately
    respects NO_COLOR, and still picks the right rendering path for a
    legitimately legacy Windows console -- forcing terminal mode doesn't
    change either of those). Also force it under `pre-commit`/CI, whose
    log viewers commonly render ANSI even though the pipe itself isn't a
    TTY, matching what the original design called for.
    """
    try:
        is_tty = sys.stdout.isatty()
    except (AttributeError, ValueError):
        is_tty = False
    running_in_ci = bool(os.environ.get("PRE_COMMIT") or os.environ.get("CI"))
    return Console(force_terminal=True if (is_tty or running_in_ci) else None)


def _run_hook_command(args: argparse.Namespace, console: Console) -> int:
    root = git.repo_root()
    if root is None:
        console.print("[red]Not inside a git repository.[/red]")
        return 1
    ok, message = hook.uninstall(root) if args.uninstall_hook else hook.install(root)
    console.print(message)
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    console = _make_console()

    if args.install_hook or args.uninstall_hook:
        return _run_hook_command(args, console)

    files = _resolve_files(args)
    if files is None:
        console.print("Not inside a git repository, and no paths were given. Nothing to check.")
        return 0

    files = [f for f in files if f.is_file()]
    if not files:
        console.print("Nothing staged to check. (Stage some files, or pass paths / --all.)")
        return 0

    results = run_all(files)
    passed = overall_passed(results, strict=args.strict)

    console.print(f"bappa-check {__version__} - {len(files)} file(s) checked\n")
    _print_checklist(console, results)
    console.print()

    do_animate = animate.should_animate(args.no_anim)

    if passed:
        animate.play(console, style="bold green", animate=do_animate)
        console.print(art.success_badge())
    else:
        fail_count = sum(1 for r in results for f in r.findings if f.severity == Severity.FAIL)
        hint = f"fix the {fail_count} issue{'s' if fail_count != 1 else ''} above"
        if not args.strict and any(r.severity == Severity.WARN for r in results):
            hint += ", or run without --strict"
        animate.play(console, style="bold red", animate=do_animate)
        console.print(art.failure_badge(hint))

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
