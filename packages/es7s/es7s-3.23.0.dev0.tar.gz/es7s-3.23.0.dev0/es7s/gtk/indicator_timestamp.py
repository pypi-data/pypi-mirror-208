# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import time

import pytermor as pt

from ._base import _BaseIndicator, _BoolState, CheckMenuItemConfig
from ..shared import SocketMessage, get_config
from ..shared.dto import TimestampInfo


class IndicatorTimestamp(_BaseIndicator[TimestampInfo]):
    """ 
    ╭──────────╮                         ╭────────────╮
    │ Δ │ PAST │                         │ ∇ │ FUTURE │
    ╰──────────╯                         ╰────────────╯
             -1h  -30min   ṇọẉ   +30min  +1h
           ▁▁▁┌┴┐▁▁▁▁┌┴┐▁▁▁▁┌┴┐▁▁▁▁┌┴┐▁▁▁▁┌┴┐▁▁▁
       ⠄⠢⠲░░░░│▁│░░░░│▃│░░░░│█│░░░░│▀│░░░░│▔│░⣊⠈⣁⢉⠠⠂⠄
          ▔▔▔▔└┬┘▔▔▔▔└┬┘▔▔▔▔└┬┘▔▔▔▔└┬┘▔▔▔▔└┬┘▔▔▔▔
             ← 0%   +50%   +100%    |      |
                           -100%  -50%    -0% →

    """
    def __init__(self):
        self.config_section = "indicator.timestamp"
        self._formatter = pt.dual_registry.get_by_max_len(6)
        self._formatter._allow_fractional = False  # @FIXME (?) copied from monitor

        self._show_value = _BoolState(config_var=(self.config_section, "label-value"))

        super().__init__(
            "timestamp",
            icon_name_default="delta_0.png",
            icon_path_dynamic_tpl="delta_%d.png",
            icon_thresholds=[
                95,
                *range(90, -91, -10),
                -95,
            ],
            title="Time delta",
        )

    def _init_state(self):
        super()._init_state()
        self._state_map.update(
            {
                CheckMenuItemConfig(
                    "Show value (ms/../years)", separator_before=True
                ): self._show_value,
            }
        )

    def _render(self, msg: SocketMessage[TimestampInfo]):
        now = time.time()
        if (remote := msg.data.ts) is None:
            self._render_result("--", "--", True, self._icon_name_default)
            return

        period = 3600
        if now >= remote:
            minp = 0.00
            maxp = 1.00
            ref = now - period
        else:
            minp = -0.95
            maxp = -0.00
            ref = now + period

        rel = (remote - ref)/period
        relp = max(minp, min(maxp, rel))
        valuep = int(100*relp)


        delta_str = ""
        if self._show_value:
            delta_str = self._formatter.format(now - remote)
            if get_config().get_indicator_debug_mode():
                delta_str += f"{rel:.3f} {self._select_icon(valuep)}"

        self._render_result(
            delta_str,
            delta_str,
            False,
            icon=self._select_icon(valuep),
        )
