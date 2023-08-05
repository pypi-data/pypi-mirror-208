# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from pytermor import format_auto_float

from ._base import _BaseIndicator, _BoolState, CheckMenuItemConfig
from ..shared import SocketMessage
from ..shared.dto import MemoryInfo, DiskUsageInfo


class IndicatorDiskUsage(_BaseIndicator[MemoryInfo]):
    def __init__(self):
        self.config_section = "indicator.disk"

        self._show_perc = _BoolState(config_var=(self.config_section, "label-used"))
        self._show_bytes = _BoolState(config_var=(self.config_section, "label-free"))

        super().__init__(
            "disk",
            icon_name_default="disk-0.svg",
            icon_path_dynamic_tpl="disk-%d.svg",
            icon_thresholds=[
                100,
                99,
                98,
                95,
                92,
                *range(90, 0, -10),
            ],
            title="Disk usage",
        )

    def _init_state(self):
        super()._init_state()
        self._state_map.update({
            CheckMenuItemConfig("Show used (%)", separator_before=True): self._show_perc,
            CheckMenuItemConfig("Show free (GB/TB)"): self._show_bytes,
        })

    def _render(self, msg: SocketMessage[DiskUsageInfo]):
        used_ratio = msg.data.used_perc/100
        warning = used_ratio >= 0.90  # @todo
        self._render_result(
            self._format_result(used_ratio, msg.data.free),
            self._format_result(100, 1e10),
            warning,
            self._select_icon(100 * used_ratio),
        )

    def _format_result(self, used_ratio: float, free: float) -> str:
        parts = []
        if self._show_perc:
            parts += [f"{100 * used_ratio:3.0f}% "]
        if self._show_bytes:
            parts += ["".join(self._format_free_value(round(free)))]
        return " ".join(parts).rstrip()

    def _format_free_value(self, free: int) -> tuple[str, str]:
        free_gb = free / 1000**3
        free_tb = free / 1000**4
        if free_gb < 1:
            return "< 1G", ""
        if free_gb < 1000:
            return format_auto_float(free_gb, 3, False), "G"
        return format_auto_float(free_tb, 3, False), "T"
