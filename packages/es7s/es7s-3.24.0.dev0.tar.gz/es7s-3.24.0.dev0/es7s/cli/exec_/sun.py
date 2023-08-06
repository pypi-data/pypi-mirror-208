# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from __future__ import annotations

import io
import sys
import typing as t
from collections import OrderedDict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta, time

import pytermor as pt

from es7s.shared import Styles as BaseStyles, get_stdout, SunCalc, IoProxy, FrozenStyle
from es7s.shared.io import make_interceptor_io
from es7s.shared.struct import DoublyLinkedNode, RingList
from .._base_opts_params import FloatRange, DayMonthOption, OPTION_DEFAULT, IntRange
from .._decorators import _catch_and_log_and_exit, cli_option, cli_command, _preserve_terminal_state
from .._terminal_state import TerminalStateController


class _Styles(BaseStyles):
    BG_NIGHT = 17
    BG_MORNING = 26
    BG_DAY = 229
    BG_EVENING = 217

    BG_NIGHT_TO_MORNING = [18, 19]
    BG_MORNING_TO_DAY = [111, 223]
    BG_DAY_TO_EVENING = [223, 217]
    BG_EVENING_TO_NIGHT = [89, 53]

    TEXT_SCALE_BORDER = pt.cv.GRAY_23
    TEXT_SCALE_DEFAULT = pt.cv.GRAY_35
    TEXT_SCALE_NOW = pt.cv.GRAY_100

    FMT_SCALE_BORDER = FrozenStyle(fg=TEXT_SCALE_BORDER, overlined=True)
    FMT_SCALE_DEFAULT = FrozenStyle(fg=TEXT_SCALE_DEFAULT, overlined=True)
    FMT_SCALE_NOW = FrozenStyle(fg=TEXT_SCALE_NOW, blink=True)

@dataclass
class TimeType:
    icon: str
    display_name: str
    fill_color: int | None = None
    scale_fallback_char: str = None

    def __hash__(self) -> int:
        return hash(self.icon + self.display_name)


TT_DAWN = TimeType("🌃", "Dawn", _Styles.BG_MORNING, "▒")
TT_SUNRISE = TimeType("🌄", "Sunrise", _Styles.BG_DAY, "█")
TT_SUNSET = TimeType("🌇", "Sunset", _Styles.BG_EVENING, "▓")
TT_DUSK = TimeType("🌆", "Dusk", _Styles.BG_NIGHT, "░")
TT_NOW = TimeType("--", "Now -->")

TIME_TYPES = OrderedDict[str, TimeType](
    {
        "dawn": TT_DAWN,
        "sunrise": TT_SUNRISE,
        "sunset": TT_SUNSET,
        "dusk": TT_DUSK,
    }
)

TIME_TYPE_TRANSITIONS: dict[tuple[TimeType, TimeType], list[int]] = {
    (TT_DUSK, TT_DAWN): _Styles.BG_NIGHT_TO_MORNING,
    (TT_DAWN, TT_SUNRISE): _Styles.BG_MORNING_TO_DAY,
    (TT_SUNRISE, TT_SUNSET): _Styles.BG_DAY_TO_EVENING,
    (TT_SUNSET, TT_DUSK): _Styles.BG_EVENING_TO_NIGHT,
    (TT_DAWN, TT_DUSK): _Styles.BG_EVENING_TO_NIGHT,
    (TT_SUNSET, TT_SUNRISE): reversed(_Styles.BG_DAY_TO_EVENING),
}


@dataclass
class TimeDef(DoublyLinkedNode):
    timetype: TimeType
    time: time = None

    def __str__(self):
        return f"{self.time.strftime('%T')} ({self.timetype.display_name:>7s})"


@cli_command(
    name=__file__,
    short_help="display sunrise and sunset timings",
    command_examples=[
        f"%s {s}\n"
        for s in (
            "--date Nov-15",
            "--date 11-15",
            "--date 15-Nov --lat 52.12 --long 36.32",
            "--date 15nov --lat 90.00 --long 00.00",
        )
    ],
)
@cli_option("-d", "--date", cls=DayMonthOption, help=OPTION_DEFAULT)
@cli_option(
    "-φ",
    "--lat",
    type=FloatRange(-90, 90),
    default=55.755833,
    show_default=True,
    help="A coordinate that specifies the north–south position of a point of interest.",
)
@cli_option(
    "-λ",
    "--long",
    type=FloatRange(-180, 180),
    default=37.617222,
    show_default=True,
    help="A coordinate that specifies the east–west position of a point of interest.",
)
@cli_option(
    "-A",
    "--auto-update",
    is_flag=True,
    show_default=True,
    help="Enable auto-update infinite loop mode.",
)
@cli_option(
    "-M",
    "--margin",
    type=IntRange(0, max_open=True),
    default=1,
    show_default=True,
    help="Number of spaces on each side of the output.",
)
@cli_option(
    "-I",
    "--interval",
    type=FloatRange(0.0, max_open=True),
    default=1.0,
    show_default=True,
    help="Delay between frame renderings. Ignored if not an auto-update mode.",
)
@_catch_and_log_and_exit
@_preserve_terminal_state
class SunCommand:
    """
    @TODO curl ip-api.com -> geolocation [timeout 1s, disablable]
    """

    RESOLUTION_X = 24

    PAD_VERT = pt.pad(1)
    GAP_VERT = pt.pad(2)
    COLUMN_PAD = pt.pad(5)

    def __init__(
        self,
        tstatectl: TerminalStateController,
        date: datetime | None,
        lat: float,
        long: float,
        auto_update: bool,
        margin: int,
        interval: float,
    ):
        self._date = date
        self._lat = lat
        self._long = long
        self._auto_update = auto_update
        self._margin = margin
        self._interval = interval

        self._is_today = self._date is None
        self._sun_calc = SunCalc()

        self._run(tstatectl)

    def _run(self, tstatectl):
        if not self._auto_update:
            self._render(get_stdout())
            return

        import select
        stdout = get_stdout()

        tstatectl.hide_cursor()
        tstatectl.enable_alt_screen_buffer()
        tstatectl.disable_input()

        interceptor = io.StringIO()
        iio = make_interceptor_io(interceptor)

        show_hint_timeout = 0.0

        while True:
            interceptor.truncate(0)

            iio.echo(pt.make_reset_cursor())
            iio.echo(pt.make_clear_display())
            self._render(iio)

            interceptor.seek(0)
            content_height = interceptor.read().count("\n") - self._margin

            if show_hint_timeout > 0:
                scale_width = self._charph * self.RESOLUTION_X + 1
                popup_content = "Press R to refresh, Q to exit"
                popup_width = min(len(popup_content) + 4, scale_width)
                popup_margin = max(0, (scale_width - popup_width) // 2)
                iio.echo(
                    pt.make_set_cursor(
                        max(1, self._margin + content_height // 2 - 1),
                        self._margin + popup_margin,
                    )
                )
                iio.echo_rendered(
                    popup_content.center(popup_width),
                    FrozenStyle(fg="hi-white", bg=pt.cv.NAVY_BLUE),
                )
                show_hint_timeout = max(0, show_hint_timeout - self._interval)

            interceptor.seek(0)
            stdout.echo(interceptor.read(), newline=False)

            i, _, _ = select.select([sys.stdin], [], [], self._interval)
            if i:
                match (key := sys.stdin.read(1)[0]):
                    case "q":
                        raise SystemExit
                    case "r":
                        continue
                    case _:
                        show_hint_timeout = 2.0

    def _render(self, io: IoProxy):
        self._now = datetime.now()
        self._is_daytime = None

        # chars per hour
        self._charph = (pt.get_terminal_width() - self._margin * 2) // self.RESOLUTION_X
        self._charph = min(6, self._charph)

        dt = self._now
        if self._date:
            dt = datetime(self._now.year, self._date.month, self._date.day)

        times: dict[str, datetime] = self._sun_calc.get_times(dt, self._lat, self._long)
        sunrise: datetime = times.get("sunrise")
        sunset: datetime = times.get("sunset")

        dt12 = datetime(dt.year, dt.month, dt.day, hour=12)
        _, altitude = self._sun_calc.get_position(dt12, self._lat, self._long)
        self._is_daytime = altitude > 0

        def padx(s: any) -> str:
            return (" " * self._margin) + str(s)

        def pady() -> str:
            return " " * max(1, self._margin)

        left_lines = [
            self._echo_date(io, dt),
            self._echo_location(io, self._lat, self._long),
            self._echo_duration(io, "Day length", sunset, sunrise),
        ]

        def get_max_line_len(lines):
            return max(len(pt.apply_filters(line, pt.EscSeqStringReplacer)) for line in lines)

        times_filtered = {k: v for k, v in times.items() if k in TIME_TYPES.keys() and v}
        times_ordered: OrderedDict[TimeType, datetime] = OrderedDict[TimeType, datetime]()

        time_now = {TT_NOW: self._now}
        if self._is_today:
            times_ordered.update(time_now)
        for idx, (k, tt) in enumerate(TIME_TYPES.items()):
            dt = times_filtered.get(k)
            if not dt:
                continue
            times_ordered.update({tt: dt})
            if self._is_today and dt.time() < self._now.time():
                times_ordered.move_to_end(TT_NOW)

        right_lines = [
            *self._render_vertical(io, times_ordered),
        ]
        left_max = get_max_line_len(left_lines)
        right_max = get_max_line_len(right_lines)

        for line in pady():
            io.echo(line)

        if left_max + len(self.COLUMN_PAD) + right_max >= pt.get_terminal_width():
            for line in [*left_lines, "", *right_lines]:
                io.echo(padx(line))
        else:
            while left_lines or right_lines:
                left_line = left_lines.pop(0) if left_lines else ""
                left_line += max(0, left_max - get_max_line_len([left_line])) * " "
                right_line = right_lines.pop(0) if right_lines else ""
                io.echo(padx(left_line) + self.COLUMN_PAD + right_line)
        io.echo()

        self._render_horizontal(io, times_ordered, dt12)

    def _render_vertical(
        self, io: IoProxy, times_ordered: OrderedDict[TimeType, datetime]
    ) -> t.Iterable[str]:
        for idx, (tt, dt) in enumerate(times_ordered.items()):
            if not self._is_today:
                show_delta = False
            else:
                time_now_idx = [*times_ordered.keys()].index(TT_NOW)
                if time_now_idx == len(times_ordered) - 1:
                    show_delta = idx == 0
                else:
                    show_delta = idx == time_now_idx + 1
            yield self._echo_time(io, tt, dt, show_delta)

    def _render_horizontal(
        self, io: IoProxy, times_ordered: OrderedDict[TimeType, datetime], dt12: datetime
    ):
        if self._charph < 1:
            warnmsg = "Terminal is too small, minimum required width: %d"
            io.echo_rendered(warnmsg % (self.RESOLUTION_X + self._margin * 2), _Styles.WARNING)
            return

        time_now = times_ordered.pop(TT_NOW, None)
        time_defs = RingList[TimeDef]()
        time_def_earliest: TimeDef | None = None
        for tt, dt in times_ordered.items():
            tdef = TimeDef(timetype=tt, time=dt.time())
            if time_def_earliest is None or tdef.time < time_def_earliest.time:
                time_def_earliest = tdef
            time_defs.insert(tdef)

        if len(time_defs) == 0:
            time_def_earliest = TimeDef(
                timetype=TT_SUNRISE if self._is_daytime else TT_DUSK,
                time=dt12.time(),
            )
            time_def_earliest.connect(time_def_earliest)

        dt_cur = datetime.combine(date=dt12, time=time())
        scale_colors: list[int] = []
        scale_fallback_chars: list[str] = []
        scale_marks: list[str] = []
        scale_digits: list[str] = []
        scale_digits_queue: deque[str] = deque()
        transition_queue: deque[int] = deque()
        tdef: TimeDef = time_def_earliest.prev
        allowed_to_cross_midnight: bool = True
        now_idx = None

        SCALE_TOP_CHAR = "▁"
        SCALE_CHAR = "█"
        SCALE_CHAR_NOW = "┃" if self._charph > 1 else "│"
        SCALE_CHAR_LEFT_BORDER  = "▐" if io.sgr_allowed else "▌"
        SCALE_CHAR_RIGHT_BORDER = "▌" if io.sgr_allowed else "▐"

        SCALE_MARK_CHAR = " "
        SCALE_MARK_CHAR_LEFT_BORDER = "▌"
        SCALE_MARK_CHAR_RIGHT_BORDER = "▐"
        SCALE_MARK_CHAR_HOUR = "╵"
        SCALE_MARK_CHAR_N_HOURS = "╹"
        SCALE_MARK_CHAR_TIME_TYPE = "△"
        SCALE_MARK_CHAR_NOW = "▲"

        def padx(s: str) -> str:
            return f"{pt.pad(self._margin)}{s}{pt.pad(self._margin)}"

        def render_scale():
            def iter_scale():
                for idx, c in enumerate(scale_colors):
                    char = SCALE_CHAR
                    if not io.sgr_allowed:
                        char = scale_fallback_chars[idx]

                    fg = pt.Color256.get_by_code(c)
                    bg = pt.NOOP_COLOR
                    fmt = pt.Style(fg=fg, bg=bg)

                    if idx == 0:
                        char = SCALE_CHAR_LEFT_BORDER
                        fmt.bg = _Styles.TEXT_SCALE_BORDER
                    if idx == len(scale_colors) - 1:
                        char = SCALE_CHAR_RIGHT_BORDER
                        fmt.bg = _Styles.TEXT_SCALE_BORDER
                    elif idx == now_idx:
                        char = SCALE_CHAR_NOW
                        fmt.bg = fmt.fg
                        fmt.blink = True
                        fmt.autopick_fg()

                    yield io.render(char, fmt)

            return "".join(iter_scale())

        while True:
            scale_mark_char = SCALE_MARK_CHAR
            scale_mark_fmt = _Styles.FMT_SCALE_DEFAULT

            if self._charph >= 2 and dt_cur.time().minute == 0:
                scale_mark_char = SCALE_MARK_CHAR_HOUR
                each_n_hours = 4 if self._charph >= 4 else 6
                if (cur_hour := dt_cur.time().hour) % each_n_hours == 0:
                    scale_mark_char = SCALE_MARK_CHAR_N_HOURS
                    scale_digits_queue.extend(str(cur_hour))

            if dt_cur.time() > tdef.next.time and (
                tdef.next.time > tdef.time or allowed_to_cross_midnight
            ):
                transition = TIME_TYPE_TRANSITIONS.get((tdef.timetype, tdef.next.timetype))
                tdef = tdef.next

                if not transition and tdef.timetype != tdef.next.timetype:
                    transition = [pt.cv.GRAY_3.code, pt.cv.RED_3.code, pt.cv.GRAY_3.code]
                if transition:
                    transition_queue.extend(transition)
                    scale_mark_char = SCALE_MARK_CHAR_TIME_TYPE
                allowed_to_cross_midnight = False

            if len(scale_colors) == 0:
                scale_mark_char = SCALE_MARK_CHAR_LEFT_BORDER
                scale_mark_fmt = _Styles.FMT_SCALE_BORDER

            if len(transition_queue):
                scale_colors.append(transition_queue.popleft())
            else:
                scale_colors.append(tdef.timetype.fill_color)
            scale_fallback_chars.append(tdef.timetype.scale_fallback_char)

            last_iteration = dt_cur.date() != dt12.date()
            if last_iteration:
                scale_mark_char = SCALE_MARK_CHAR_RIGHT_BORDER
                scale_mark_fmt = _Styles.FMT_SCALE_BORDER

            if time_now is not None and (dt_cur.time() >= time_now.time() or last_iteration):
                time_now = None
                now_idx = len(scale_colors) - 1
                scale_mark_char = SCALE_MARK_CHAR_NOW
                scale_mark_fmt = _Styles.FMT_SCALE_NOW

            if len(scale_digits_queue):
                scale_digits.append(scale_digits_queue.popleft())
            else:
                scale_digits.append(" ")

            scale_marks.append(io.render(scale_mark_char, scale_mark_fmt))

            if last_iteration:
                break

            dt_cur += timedelta(seconds=60 * 60 / self._charph)

        io.echo(padx(io.render(SCALE_TOP_CHAR * len(scale_marks), _Styles.FMT_SCALE_BORDER)))
        io.echo(padx(render_scale()))
        io.echo(padx("".join(scale_marks)))
        io.echo(padx(pt.render(
            "".join(scale_digits), FrozenStyle(fg=_Styles.TEXT_SCALE_DEFAULT)
        )))

    def _echo_location(self, io: IoProxy, lat: float, long: float) -> str:
        text = pt.Text()
        self._append_label_long(text, "Location")
        self._append_note(text, f"{lat:.3f}, {long:.3f}")
        return io.render(text)

    def _echo_date(self, io: IoProxy, dt: datetime) -> str:
        text = pt.Text()
        self._append_label_long(text, "Date")
        self._append_note(text, f"{dt:%-e-%b-%y}")
        return io.render(text)

    def _echo_duration(
        self, io: IoProxy, label: str, sunset: datetime | None, sunrise: datetime | None
    ) -> str:
        if sunset and sunrise:
            day_length = sunset - sunrise
            delta_str = pt.format_time_delta(day_length.total_seconds(), 10)
        else:
            delta_str = "polar " + ("day" if self._is_daytime else "night")

        text = pt.Text()
        self._append_label_long(text, label)
        self._append_note(text, delta_str)
        return io.render(text)

    def _echo_time(self, io: IoProxy, tt: TimeType, dt: datetime, show_delta: bool) -> str:
        text = pt.Text()
        self._append_label(text, tt.icon, tt.display_name)
        if not dt:
            self._append_note(text, "--")
            return get_stdout().render(text)
        self._append_value(text, dt.strftime("%T"), tt)

        if show_delta:
            delta = dt - self._now
            next_str = ""
            if delta.total_seconds() < 0:
                delta += timedelta(days=1)
                next_str = " (next)"
            delta_str = pt.format_time_delta(delta.total_seconds(), 6) + next_str
            self._append_delta(text, f"Δ {delta_str}")

        return io.render(text)

    def _append_label_long(self, text: pt.Text, string: str):
        text += pt.Fragment(f"{self.PAD_VERT}{string:>10s}{self.GAP_VERT}", _Styles.TEXT_LABEL)

    def _append_label(self, text: pt.Text, icon: str, string: str):
        text += pt.Fragment(
            f"{self.PAD_VERT}{icon} {string:<7s}" + self.GAP_VERT, _Styles.TEXT_LABEL
        )

    def _append_value(self, text: pt.Text, string: str, tt: TimeType):
        st = _Styles.TEXT_DEFAULT
        if tt == TT_NOW:
            st = _Styles.TEXT_ACCENT
        text += pt.Fragment(string + self.GAP_VERT, st)

    def _append_note(self, text: pt.Text, string: str):
        text += pt.Fragment(string, _Styles.TEXT_DEFAULT)

    def _append_delta(self, text: pt.Text, string: str):
        text += pt.Fragment(string, _Styles.TEXT_LABEL)
