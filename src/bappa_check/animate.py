"""Play the Ganesha animation, with safe fallbacks for non-interactive output.

`pre-commit` captures hook output rather than attaching a real TTY, and CI
logs aren't interactive either -- in both cases we skip straight to printing
the final frame instead of trying (and failing, or just wasting time) to
animate.
"""

from __future__ import annotations

import os
import sys
import time
from typing import TextIO

from rich.console import Console
from rich.live import Live

from bappa_check import art

DEFAULT_FPS = 10


def should_animate(no_anim_flag: bool = False, stream: TextIO | None = None) -> bool:
    """Whether to actually animate, given the --no-anim flag / env / TTY-ness."""
    if no_anim_flag or os.environ.get("BAPPA_NO_ANIM"):
        return False
    stream = stream if stream is not None else sys.stdout
    try:
        return bool(stream.isatty())
    except (AttributeError, ValueError):
        return False


def play(
    console: Console,
    *,
    style: str = "bold green",
    frames: list[list[str]] | None = None,
    fps: int = DEFAULT_FPS,
    animate: bool = True,
) -> None:
    """Render the Ganesha animation, ending on a permanent final frame.

    When `animate` is False, skips straight to printing the final frame --
    used for --no-anim, BAPPA_NO_ANIM, and non-TTY output.
    """
    frames = frames if frames is not None else art.build_animation_frames()
    if not frames:
        return

    if animate:
        delay = 1.0 / fps
        with Live(console=console, refresh_per_second=fps, transient=True) as live:
            for frame in frames:
                live.update(art.ganesha(frame, style=style))
                time.sleep(delay)

    console.print(art.ganesha(frames[-1], style=style))
