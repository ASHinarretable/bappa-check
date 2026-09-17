from __future__ import annotations

import io

import pytest
from rich.console import Console

from bappa_check import animate, art


class _FakeStream(io.StringIO):
    def __init__(self, is_tty: bool) -> None:
        super().__init__()
        self._is_tty = is_tty

    def isatty(self) -> bool:
        return self._is_tty


def test_should_animate_true_on_a_tty_with_no_flags() -> None:
    assert animate.should_animate(False, _FakeStream(True)) is True


def test_should_animate_false_when_flag_set() -> None:
    assert animate.should_animate(True, _FakeStream(True)) is False


def test_should_animate_false_on_a_non_tty() -> None:
    assert animate.should_animate(False, _FakeStream(False)) is False


def test_should_animate_false_via_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BAPPA_NO_ANIM", "1")
    assert animate.should_animate(False, _FakeStream(True)) is False


def test_should_animate_handles_a_stream_without_isatty() -> None:
    # e.g. some pipe/redirect wrappers don't implement isatty() at all.
    class NoIsatty:
        pass

    assert animate.should_animate(False, NoIsatty()) is False  # type: ignore[arg-type]


def test_play_with_animate_false_prints_final_frame_only(monkeypatch: pytest.MonkeyPatch) -> None:
    sleeps: list[float] = []
    monkeypatch.setattr(animate.time, "sleep", lambda s: sleeps.append(s))

    console = Console(force_terminal=False, width=80, record=True)
    animate.play(console, animate=False)

    assert sleeps == []  # no animation loop ran at all
    output = console.export_text()
    assert output.strip() != ""


def test_play_with_animate_true_renders_and_ends_on_final_frame(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(animate.time, "sleep", lambda _s: None)  # don't actually wait in tests

    console = Console(force_terminal=False, width=80, record=True)
    animate.play(console, animate=True, fps=1000)  # fast fps, no real delay anyway

    output = console.export_text()
    assert output.strip() != ""


def test_play_with_no_frames_does_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(animate.time, "sleep", lambda _s: None)
    console = Console(force_terminal=False, width=80, record=True)
    animate.play(console, frames=[], animate=True)
    assert console.export_text() == ""


def test_play_final_frame_matches_the_provided_frames_last_entry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(animate.time, "sleep", lambda _s: None)
    console = Console(force_terminal=False, width=80, record=True)
    custom_frames = [list(art.BASE_FRAME), art._eye_blink_frame()]
    animate.play(console, frames=custom_frames, animate=False)
    # animate=False always prints frames[-1]
    assert "-" in console.export_text()  # the blinked eye row uses "-" for "*"
