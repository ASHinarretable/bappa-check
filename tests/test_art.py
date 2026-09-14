from __future__ import annotations

import string

from rich.console import Console

from bappa_check import art


def test_frame_is_non_empty() -> None:
    assert art.BASE_FRAME
    assert art.FRAME_HEIGHT == len(art.BASE_FRAME)


def test_all_lines_share_the_same_width() -> None:
    # Equal width matters for centering and for future animation frames
    # (shifting the trunk etc.) not to jitter the figure sideways.
    widths = {len(line) for line in art.BASE_FRAME}
    assert widths == {art.FRAME_WIDTH}


def test_frame_is_pure_ascii() -> None:
    allowed = set(string.printable)
    for line in art.BASE_FRAME:
        assert set(line) <= allowed, f"non-ASCII/printable char in: {line!r}"


def test_render_frame_default_matches_base_frame() -> None:
    assert art.render_frame() == "\n".join(art.BASE_FRAME)
    assert art.render_frame().count("\n") == art.FRAME_HEIGHT - 1


def test_render_frame_accepts_a_custom_frame() -> None:
    custom = ["abc", "def"]
    assert art.render_frame(custom) == "abc\ndef"


def test_ganesha_renders_without_crashing_on_a_plain_console() -> None:
    console = Console(file=None, force_terminal=False, width=80, record=True)
    console.print(art.ganesha())
    output = console.export_text()
    assert output.strip() != ""


def test_success_badge_contains_the_expected_text() -> None:
    console = Console(force_terminal=False, width=80, record=True)
    console.print(art.success_badge())
    assert "BAPPA APPROVED" in console.export_text()


def test_failure_badge_contains_hint_and_message() -> None:
    console = Console(force_terminal=False, width=80, record=True)
    console.print(art.failure_badge("fix your 2 issues"))
    output = console.export_text()
    assert "BAPPA SAYS: NOT YET" in output
    assert "fix your 2 issues" in output


def test_badges_are_pure_ascii_too() -> None:
    console = Console(force_terminal=False, width=80, record=True)
    console.print(art.success_badge())
    console.print(art.failure_badge())
    output = console.export_text()
    assert all(ord(c) < 128 for c in output)
