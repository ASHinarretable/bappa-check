"""ASCII Ganesha artwork — the reference frame the user supplied.

Kept as pure ASCII (checked: no non-ASCII bytes, no BOM) so it renders
identically on Windows cmd/PowerShell, macOS Terminal, and CI logs.
Every line is padded to the same width so it centers cleanly in a
Rich Panel and so future animation frames (trunk sway, eye blink,
sparkle ring) can be derived from it without jitter.
"""

from __future__ import annotations

from rich import box
from rich.align import Align
from rich.console import RenderableType
from rich.panel import Panel

BASE_FRAME: list[str] = [
    '                                            ',
    '                     ..                     ',
    '                    -===                    ',
    '                .::-==+=--:.                ',
    '              :-----:.::-----.              ',
    '             ----:::-::-::----:             ',
    '            -=--:--=++++=-------            ',
    '           .-=:-=++++++++++=-:=-.           ',
    '            :-**=:.      .:=**-.            ',
    '        -#%%%#**:.  .::.  .:#*#%%%#.        ',
    '      =#**#++*%*-***----***=*%*++#*##:      ',
    '        --*+=+#*:+*=----=*+:+#+=+*-         ',
    '         ==*+=#*.::......-:.*#=+*=-         ',
    '          :=***#+*-......-*+#***=.          ',
    '            -+++=-..::-:.:-=**+-            ',
    '              =  .+:-===-*:  +              ',
    '                   ====-:                   ',
    '                   -+*+-:   ..              ',
    '                    =####*##*#*-            ',
    '                       :-.  :-=*.           ',
    '                             +=             ',
    '                                            ',
    '                                            ',
    '                                            ',
    '           .      .                         ',
]

FRAME_WIDTH = max(len(line) for line in BASE_FRAME)
FRAME_HEIGHT = len(BASE_FRAME)


def render_frame(frame: list[str] | None = None) -> str:
    """Join a frame's lines into a single block of text."""
    return "\n".join(frame if frame is not None else BASE_FRAME)


# --- Animation -------------------------------------------------------------
#
# Every derived frame keeps the figure itself byte-identical to BASE_FRAME.
# Two safe, narrow edits produce the whole animation:
#   1. a sparkle drifts through the fully-blank rows above/below the figure
#      (never touches a drawn character at all)
#   2. one eye-blink frame swaps the two "*" pairs on the eye row for "-"
# Row/column positions are discovered from BASE_FRAME itself, not hardcoded,
# so this keeps working if the art file above ever changes.

_BLANK_ROWS = [i for i, line in enumerate(BASE_FRAME) if not line.strip()]
_EYE_ROW = 8
_EYE_COLUMNS = [i for i, ch in enumerate(BASE_FRAME[_EYE_ROW]) if ch == "*"]
_SPARKLE_COLUMNS = [10, 18, 26, 34]


def _with_char(frame: list[str], row: int, col: int, char: str) -> list[str]:
    result = list(frame)
    line = list(result[row])
    if 0 <= col < len(line):
        line[col] = char
    result[row] = "".join(line)
    return result


def _sparkle_frame(row: int, col: int) -> list[str]:
    return _with_char(BASE_FRAME, row, col, "*")


def _eye_blink_frame() -> list[str]:
    frame = list(BASE_FRAME)
    line = list(frame[_EYE_ROW])
    for col in _EYE_COLUMNS:
        line[col] = "-"
    frame[_EYE_ROW] = "".join(line)
    return frame


def build_animation_frames() -> list[list[str]]:
    """A short (~1s @ 10fps) animation loop derived from BASE_FRAME."""
    frames = [list(BASE_FRAME)]
    if len(_BLANK_ROWS) >= 2:
        top, bottom = _BLANK_ROWS[0], _BLANK_ROWS[-1]
        frames += [_sparkle_frame(top, col) for col in _SPARKLE_COLUMNS]
        frames += [_sparkle_frame(bottom, col) for col in reversed(_SPARKLE_COLUMNS)]
    if _EYE_COLUMNS:
        frames.append(_eye_blink_frame())
    frames.append(list(BASE_FRAME))
    return frames


def ganesha(frame: list[str] | None = None, *, style: str = "bold green") -> RenderableType:
    """The Ganesha figure, centered, in the given rich style."""
    return Align.center(render_frame(frame), style=style)


def success_badge() -> RenderableType:
    return Panel(
        Align.center("BAPPA APPROVED -- Ganpati Bappa Morya!"),
        style="bold white on green",
        expand=False,
        box=box.ASCII,  # never rely on the terminal supporting Unicode box-drawing
    )


def failure_badge(hint: str = "fix the issues above, or run with --strict off") -> RenderableType:
    return Panel(
        Align.center(f"BAPPA SAYS: NOT YET\n{hint}"),
        style="bold white on red",
        expand=False,
        box=box.ASCII,
    )
