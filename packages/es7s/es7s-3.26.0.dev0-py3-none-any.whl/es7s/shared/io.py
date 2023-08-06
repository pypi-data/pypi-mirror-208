# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from __future__ import annotations

import sys
import typing as t
from dataclasses import dataclass
from io import StringIO
from threading import Lock

import click
import pytermor as pt
from pytermor import FT, RT, NOOP_STYLE, SgrStringReplacer

_stdout: IoProxy | None = None
_stderr: IoProxy | None = None


@dataclass
class IoParams:
    color: bool | None = None
    tmux: bool = False


def get_stdout(require: object = True) -> IoProxy | None:
    global _stdout
    if not _stdout:
        if require:
            raise RuntimeError("Stdout proxy is uninitialized")
        return None
    return _stdout


def get_stderr(require=True) -> IoProxy | None:
    global _stderr
    if not _stderr:
        if require:
            raise RuntimeError("Stderr proxy is uninitialized")
        return None
    return _stderr


def init_io(
    io_params: IoParams = IoParams(),
    stdout: t.IO = sys.stdout,
    stderr: t.IO = sys.stderr,
) -> tuple[IoProxy, IoProxy]:
    global _stdout, _stderr
    if _stdout:
        raise RuntimeError("Stdout proxy is already initialized")
    if _stderr:
        raise RuntimeError("Stderr proxy is already initialized")

    _stdout = IoProxy(io_params, stdout)
    _stderr = IoProxy(IoParams(color=io_params.color, tmux=False), stderr)
    pt.RendererManager.set_default(_stdout.renderer)

    from . import get_logger

    get_logger().setup_stderr_proxy(_stderr)

    return _stdout, _stderr


def destroy_io():
    global _stdout, _stderr
    if _stdout:
        _stdout.destroy()
    if _stderr:
        _stderr.destroy()
    _stdout = None
    _stderr = None


def make_dummy_io() -> IoProxy:
    io = StringIO()
    io.name = "dummy_io"
    return IoProxy(IoParams(), io)


def make_interceptor_io(io: StringIO) -> IoProxy:
    io.name = "interceptor_io"
    actual_io = get_stdout()
    return IoProxy(actual_io._io_params, io, actual_io._io)


class IoProxy:
    CSI_EL0 = pt.make_clear_line_after_cursor().assemble()

    PBAR_MODE_ANY_MSG_START = pt.make_set_cursor_column(1).assemble() + CSI_EL0
    PBAR_MODE_ANY_MSG_END = pt.SeqIndex.BG_COLOR_OFF.assemble()

    _progress_bar_mode = False

    def __init__(self, io_params: IoParams, io: t.IO, actual_io: t.IO = None):
        self._io_params = io_params
        self._color = io_params.color
        self._tmux = io_params.tmux

        self._renderer = self._make_renderer(actual_io or io)
        # pass original output device for correct autodetection

        self._io = io
        self._is_stderr = io == sys.stderr
        self._broken = False
        self._click_available = False

        if actual_io:
            return  # disable click output proxying

        try:
            import click

            self._click_available = isinstance(click.echo, t.Callable)
        except ImportError:
            pass

    @property
    def io(self) -> t.IO:
        return self._io

    @property
    def renderer(self) -> pt.IRenderer:
        return self._renderer

    @property
    def color(self) -> bool:
        return self._color

    @property
    def tmux(self) -> bool:
        return self._tmux

    @property
    def sgr_allowed(self) -> bool:
        if isinstance(self._renderer, pt.SgrRenderer):
            return self._renderer.is_format_allowed
        return False

    @property
    def is_broken(self) -> bool:
        return self._broken

    def as_dict(self) -> dict:
        return {
            "renderer": self._renderer,
            "color": self._color,
            "tmux": self._tmux,
        }

    def render(self, string: RT | list[RT] = "", fmt: FT = NOOP_STYLE) -> str:
        return pt.render(string, fmt, self._renderer, no_log=self._is_stderr)

    @t.overload
    def echo_rendered(self, inp: str, style: pt.Style, *, newline=True) -> None:
        ...

    @t.overload
    def echo_rendered(self, inp: str | pt.IRenderable, *, newline=True) -> None:
        ...

    def echo_rendered(self, *args, newline=True) -> None:
        if 1 <= len(args) <= 2:
            rendered = self.render(*args[:2])
            self.echo(rendered, newline=newline)
        else:
            raise pt.ArgCountError(len(args), 1, 2)

    def echo_raw(self, string: str | pt.ISequence = "", newline: bool = True) -> None:
        if isinstance(string, pt.ISequence):
            string = ""
        else:
            string = pt.apply_filters(string, pt.EscSeqStringReplacer)
        self.echo(string, newline)


    def echo(self, string: str | pt.ISequence = "", newline: bool = True) -> None:
        if isinstance(string, pt.ISequence):
            string = string.assemble()
            newline = False

        if IoProxy._progress_bar_mode:
            string = self.PBAR_MODE_ANY_MSG_START + string + self.PBAR_MODE_ANY_MSG_END

        try:
            if isinstance(self._io, OneLineStringIO):
                self._io.truncate()

            if self._click_available:
                click.echo(string, file=self._io, color=self._color, nl=newline)
            else:
                print(
                    string,
                    file=self._io,
                    end=("\n" if newline else ""),
                    flush=not bool(string),
                )

            if isinstance(self._io, OneLineStringIO):
                self._io.seek(0)

        except BrokenPipeError:
            self._broken = True
            self._pacify_flush_wrapper()

    def echo_progress_bar(self, string: str = ""):
        self.echo(string + self.CSI_EL0, newline=False)

    def enable_progress_bar(self):
        IoProxy._progress_bar_mode = True

    def disable_progress_bar(self):
        self.echo(newline=False)  # clear the bar
        IoProxy._progress_bar_mode = False

    def write(self, s: str) -> None:
        self.echo(s)

    def destroy(self):
        pass

    def _make_renderer(self, io: t.IO) -> pt.IRenderer:
        if self.tmux:
            if self.color is False:
                return pt.renderer.NoOpRenderer()
            return pt.renderer.TmuxRenderer()
        return pt.SgrRenderer(self._output_mode, io)

    def _pacify_flush_wrapper(self) -> None:
        sys.stdout = t.cast(t.TextIO, click.utils.PacifyFlushWrapper(sys.stdout))
        sys.stderr = t.cast(t.TextIO, click.utils.PacifyFlushWrapper(sys.stderr))

    @property
    def _output_mode(self) -> pt.OutputMode:
        if self.color is None:
            return pt.OutputMode.AUTO
        if self.color:
            return pt.OutputMode.TRUE_COLOR
        return pt.OutputMode.NO_ANSI


class BrokenPipeEvent(Exception):
    pass


class OneLineStringIO(StringIO):
    pass

