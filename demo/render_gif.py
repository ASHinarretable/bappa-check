"""Render the README/reel demo GIF programmatically.

No terminal-recording tool (VHS/ttyd/ffmpeg) is available in this
environment, so instead of capturing a real terminal session, this script
draws each frame directly with Pillow -- a monospace grid on a dark
background, colored to match a typical terminal palette. It reproduces
the *actual* bappa-check output (the real checklist text and the real
animation frames from bappa_check.art), just rendered as images instead
of ANSI escape codes.

Regenerate with:
    pip install pillow
    python demo/render_gif.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from PIL import Image, ImageDraw, ImageFont

from bappa_check import __version__, art

FONT_PATH = "C:/Windows/Fonts/cascadiamono.ttf"
FONT_SIZE = 18
CHAR_W = 11
CHAR_H = 24
PAD = 24

BG = (12, 12, 16)
FG = (220, 220, 220)
DIM = (140, 140, 150)
GREEN = (60, 210, 100)
RED = (235, 90, 90)
YELLOW = (230, 200, 90)
CYAN = (100, 200, 210)

font = ImageFont.truetype(FONT_PATH, FONT_SIZE)


class Canvas:
    def __init__(self, width_chars: int, height_chars: int) -> None:
        self.width_chars = width_chars
        self.height_chars = height_chars
        self.img = Image.new(
            "RGB", (width_chars * CHAR_W + PAD * 2, height_chars * CHAR_H + PAD * 2), BG
        )
        self.draw = ImageDraw.Draw(self.img)

    def text(self, row: int, col: int, s: str, color=FG) -> None:
        x = PAD + col * CHAR_W
        y = PAD + row * CHAR_H
        self.draw.text((x, y), s, font=font, fill=color)


CHECK_ROWS = [
    ("conflict-markers", "ok", GREEN, "-"),
    ("secrets", "ok", GREEN, "-"),
    ("large-files", "ok", GREEN, "-"),
    ("syntax", "ok", GREEN, "-"),
    ("debug-leftovers", "ok", GREEN, "-"),
    ("whitespace", "ok", GREEN, "-"),
    ("todo-fixme", "ok", GREEN, "-"),
    ("external-lint", "ok", GREEN, "-"),
]

HEADER = f"bappa-check {__version__} - 1 file(s) checked"
NAME_W = max(len(n) for n, *_ in CHECK_ROWS)


def draw_prompt_and_header(c: Canvas) -> int:
    c.text(0, 0, "$ ", DIM)
    c.text(0, 2, "bappa-check", CYAN)
    c.text(2, 0, HEADER, FG)
    return 4


def draw_checklist(c: Canvas, top: int, revealed: int) -> None:
    header = f"{'check'.ljust(NAME_W)}  status  findings"
    c.text(top, 0, header, DIM)
    c.text(top + 1, 0, "-" * len(header), DIM)
    for i, (name, status, color, findings) in enumerate(CHECK_ROWS):
        row = top + 2 + i
        if i < revealed:
            c.text(row, 0, name.ljust(NAME_W), FG)
            c.text(row, NAME_W + 2, status.ljust(6), color)
            c.text(row, NAME_W + 10, findings, DIM)
        else:
            c.text(row, 0, name.ljust(NAME_W), (60, 60, 66))


def draw_ganesha(c: Canvas, top: int, frame: list[str], color) -> int:
    for i, line in enumerate(frame):
        c.text(top + i, 0, line, color)
    return top + len(frame)


def draw_badge(c: Canvas, top: int) -> None:
    text = "BAPPA APPROVED -- Ganpati Bappa Morya!"
    box_w = len(text) + 4
    c.draw.rectangle(
        [
            PAD - 4,
            PAD + top * CHAR_H - 4,
            PAD + box_w * CHAR_W - 4,
            PAD + (top + 2) * CHAR_H - 4,
        ],
        fill=(20, 90, 40),
        outline=GREEN,
        width=2,
    )
    c.text(top + 1, 2, text, (255, 255, 255))


def build_frames() -> tuple[list[Image.Image], list[int]]:
    frames: list[Image.Image] = []
    durations: list[int] = []
    height_chars = 4 + 2 + len(CHECK_ROWS) + 1 + art.FRAME_HEIGHT + 3
    width_chars = max(art.FRAME_WIDTH, len(HEADER), NAME_W + 20) + 2

    def new_canvas() -> Canvas:
        return Canvas(width_chars, height_chars)

    # 1. Checklist reveals row by row.
    for revealed in range(len(CHECK_ROWS) + 1):
        c = new_canvas()
        ganesha_top = draw_prompt_and_header(c)
        draw_checklist(c, ganesha_top, revealed)
        frames.append(c.img)
        durations.append(90)

    ganesha_top = draw_prompt_and_header(new_canvas())
    ganesha_start_row = ganesha_top + 2 + len(CHECK_ROWS) + 2

    # 2. Ganesha animation (sparkle drift + eye blink), from bappa_check.art.
    anim_frames = art.build_animation_frames()
    for i, frame in enumerate(anim_frames):
        c = new_canvas()
        draw_prompt_and_header(c)
        draw_checklist(c, ganesha_top, len(CHECK_ROWS))
        badge_top = draw_ganesha(c, ganesha_start_row, frame, GREEN)
        frames.append(c.img)
        # linger a bit longer on the very last (settled) frame
        durations.append(90 if i < len(anim_frames) - 1 else 120)

    # 3. Final frame + badge, held for a couple seconds.
    c = new_canvas()
    draw_prompt_and_header(c)
    draw_checklist(c, ganesha_top, len(CHECK_ROWS))
    badge_top = draw_ganesha(c, ganesha_start_row, art.BASE_FRAME, GREEN)
    draw_badge(c, badge_top)
    frames.append(c.img)
    durations.append(2200)

    return frames, durations


def main() -> None:
    frames, durations = build_frames()
    out_path = Path(__file__).resolve().parent / "demo.gif"
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )
    print(f"wrote {out_path} ({len(frames)} frames, {out_path.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
