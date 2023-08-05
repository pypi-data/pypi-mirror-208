# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import typing as t
from pytermor import format_auto_float

from ._base import _BaseIndicator, CheckMenuItemConfig, _BoolState, _State
from ..shared import SocketMessage, get_config
from ..shared.dto import CpuInfo


class IndicatorCpuLoad(_BaseIndicator[CpuInfo]):
    def __init__(self):
        self.config_section = "indicator.cpu-load"

        self._show_perc = _BoolState(config_var=(self.config_section, "label-current"))
        self._show_avg = _BoolState(config_var=(self.config_section, "label-average"))

        super().__init__(
            "cpu-load",
            "cpu",
            icon_name_default="cpuload-0.svg",
            icon_path_dynamic_tpl="cpuload-%d.svg",
            icon_thresholds=[
                95,
                87,
                75,
                62,
                50,
                37,
                25,
                12,
                0,
            ],
            title="CPU load",
        )

    def _init_state(self, state_map: t.Mapping[CheckMenuItemConfig, _State] = None):
        super()._init_state()
        self._state_map.update(
            {
                CheckMenuItemConfig("Show current (%)", separator_before=True): self._show_perc,
                CheckMenuItemConfig("Show average (1/5/15min)"): self._show_avg,
            }
        )

    def _render(self, msg: SocketMessage[CpuInfo]):
        self._render_result(
            self._format_result(msg.data.load_perc, *msg.data.load_avg),
            self._format_result(100, *[16.16] * len(msg.data.load_avg)),
            icon=self._select_icon(msg.data.load_perc),
        )

    def _format_result(self, perc: float, *avg: float) -> str:
        parts = []
        if self._show_perc.active:
            parts += [f"{perc:3.0f}% "]
        if self._show_avg.active:
            parts += (format_auto_float(a, 4) for a in avg)
        return " ".join(parts).rstrip()
