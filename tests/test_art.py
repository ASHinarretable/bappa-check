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


# --- Animation frames --------------------------------------------------


def _non_animated_row_indexes() -> set[int]:
    """Rows every frame must reproduce byte-for-byte from BASE_FRAME."""
    animated = set(art._BLANK_ROWS) | {art._EYE_ROW}
    return set(range(art.FRAME_HEIGHT)) - animated


def test_build_animation_frames_returns_multiple_frames() -> None:
    frames = art.build_animation_frames()
    assert len(frames) >= 8


def test_every_frame_has_the_same_shape_as_base_frame() -> None:
    for frame in art.build_animation_frames():
        assert len(frame) == art.FRAME_HEIGHT
        assert all(len(line) == art.FRAME_WIDTH for line in frame)


def test_animation_never_touches_the_actual_figure() -> None:
    # Only the blank margin rows (sparkle) and the eye row (blink) may
    # differ from BASE_FRAME -- the figure itself must be untouched in
    # every single frame, so the user's supplied art is never corrupted.
    untouchable = _non_animated_row_indexes()
    for frame in art.build_animation_frames():
        for row in untouchable:
            assert frame[row] == art.BASE_FRAME[row], f"row {row} was modified"


def test_first_and_last_frame_are_the_base_frame() -> None:
    frames = art.build_animation_frames()
    assert frames[0] == art.BASE_FRAME
    assert frames[-1] == art.BASE_FRAME


def test_eye_blink_frame_is_present_and_only_changes_eye_columns() -> None:
    frames = art.build_animation_frames()
    blink_frames = [f for f in frames if f[art._EYE_ROW] != art.BASE_FRAME[art._EYE_ROW]]
    assert len(blink_frames) == 1
    blink_row = blink_frames[0][art._EYE_ROW]
    base_row = art.BASE_FRAME[art._EYE_ROW]
    for col, (a, b) in enumerate(zip(blink_row, base_row)):
        if col in art._EYE_COLUMNS:
            assert a == "-"
        else:
            assert a == b


def test_sparkle_frames_only_add_a_single_asterisk_to_a_blank_row() -> None:
    for frame in art.build_animation_frames():
        for row in art._BLANK_ROWS:
            line = frame[row]
            if line == art.BASE_FRAME[row]:
                continue
            # Exactly one character differs, and it's a "*" replacing a space.
            diffs = [i for i, (a, b) in enumerate(zip(line, art.BASE_FRAME[row])) if a != b]
            assert len(diffs) == 1
            assert line[diffs[0]] == "*"
