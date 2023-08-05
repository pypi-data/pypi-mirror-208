# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import datetime
import os
import pickle
import re
import signal
from dataclasses import dataclass
from typing import OrderedDict

import pytermor

from ._base import _BaseIndicator, CheckMenuItemConfig, _StaticState, _BoolState, _State
from ..shared import SocketMessage, get_config
from ..shared.ipc import NullClient, IClientIPC


@dataclass
class _ExternalBoolState(_BoolState):
    ext: "_BaseIndicator" = None

    def click(self):
        phs = self.ext.public_hidden_state
        if phs.is_set():
            phs.clear()
            self._update_config(True)
        else:
            phs.set()
            self._update_config(False)


class IndicatorManager(_BaseIndicator):
    def __init__(self, indicators: list[_BaseIndicator]):
        self.config_section = "indicator.manager"
        self._indicators = indicators

        self._debug_state = _BoolState(config_var=("indicator", "debug"))
        self._label_sys_time_state = _BoolState(config_var=(self.config_section, "label-system-time"))
        self._label_self_uptime_state = _BoolState(config_var=(self.config_section, "label-self-uptime"))
        self._label_tick_nums = _BoolState(config_var=(self.config_section, "label-tick-nums"))
        self._restart_timeout_min = get_config().getint(
            self.config_section, "restart-timeout-min"
        )

        super().__init__(
            "manager",
            icon_name_default="es7s-grayscale.png",
            title="es7s/indicmgr",
        )
        self._monitor_data_buf.append(
            pickle.dumps(
                SocketMessage(data=None, timestamp=2147483647),
                protocol=pickle.HIGHEST_PROTOCOL,
            )
        )
        self._render_result("", icon=self._icon_name_default)

    def _make_socket_client(self, socket_topic: str, indicator_name: str) -> IClientIPC:
        return NullClient()

    def _restart(self, *_):
        # should be run as a service and thus
        # expected to be restarted by systemd,
        # so simply perform a suicide:
        os.kill(os.getpid(), signal.SIGINT)

    def _init_state(self):
        super()._init_state()
        self._state_map.update(
            OrderedDict[CheckMenuItemConfig, _State](
                {
                    CheckMenuItemConfig("Restart (shutdown)"): _StaticState(callback=self._restart),
                    CheckMenuItemConfig("Show system time", separator_before=True): self._label_sys_time_state,
                    CheckMenuItemConfig("Show self uptime"): self._label_self_uptime_state,
                    CheckMenuItemConfig("Show tick nums"): self._label_tick_nums,
                    CheckMenuItemConfig("Debug mode"): self._debug_state,
                }
            )
        )
        self._state_map.update(
            {
                CheckMenuItemConfig(
                    re.sub("(?i)[^\w\s/]+", "", indic.title).strip(),
                    separator_before=idx == 0,
                ): _ExternalBoolState(
                    config_var=(indic.config_section, "display"),
                    ext=indic,
                )
                for idx, indic in enumerate(reversed(self._indicators))
            }
        )

    def _on_before_update(self):
        if self._state.abs_running_time_sec // 60 >= self._restart_timeout_min:
            self._restart()

    def _render(self, msg: SocketMessage[None]):
        result = []
        if self._label_sys_time_state:
            result.append(datetime.datetime.now().strftime('%H:%M:%S'))
        if self._label_self_uptime_state:
            result.append(pytermor.format_time_ms(self._state.abs_running_time_sec * 1e3))
        if self._label_tick_nums:
            if int(self._state.abs_running_time_sec) % 14 >= 7:
                result.append(f"R {self._state.tick_render_num}")
            else:
                result.append(f"U {self._state.tick_update_num}")

        self._render_result("".join(f"[{s}]" for s in result))
