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
