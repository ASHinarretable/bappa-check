"""bappa-check command-line entry point."""

from __future__ import annotations

import argparse
import sys

from bappa_check import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bappa-check",
        description="Sanity-check your staged files before you commit.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"bappa-check {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    parser.parse_args(argv)
    # Phase 3/4 will wire up real checks here.
    print("bappa-check scaffold is alive.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
