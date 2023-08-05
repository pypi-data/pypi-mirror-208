# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import subprocess
from subprocess import CalledProcessError

import pytermor as pt

from ._base import (
    _BaseIndicator,
    _BoolState,
    CheckMenuItemConfig,
    _StaticState,
    _State,
    MenuItemConfig,
)
from ..shared import SocketMessage, get_logger, get_config
from ..shared.dto import ShocksInfo
from ..shared.strutil import to_subscript


class IndicatorShocks(_BaseIndicator):
    SYSTEMCTL_CALL_TIMEOUT_SEC = 60

    def __init__(self):
        self.config_section = "indicator.shocks"

        self._restart = _StaticState(callback=self._enqueue_restart)
        self._show_lat = _BoolState(config_var=(self.config_section, "label"))
        self._latency_warning_threshold_ms = get_config().getint(
            self.config_section, "latency-warn-threshold-ms"
        )

        super().__init__(
            "shocks",
            icon_name_default="shocks.svg",
            icon_path_dynamic_tpl="shocks-%s.svg",
            title="SSH/SOCKS proxy",
        )

    def _init_state(self):
        super()._init_state()
        self._state_map.update(
            {
                MenuItemConfig("Restart es7s/shocks ⚡", separator_before=False): self._restart,
                CheckMenuItemConfig("Show latency (sec)", separator_before=True): self._show_lat,
            }
        )

    def _restart_service(self):
        self._state.wait_timeout = self.SYSTEMCTL_CALL_TIMEOUT_SEC

        out, err = None, None
        try:
            try:
                cp = subprocess.run(
                    ["systemctl", "restart", "es7s-shocks"],
                    capture_output=True,
                    timeout=self.SYSTEMCTL_CALL_TIMEOUT_SEC,
                    check=True,
                )
            except CalledProcessError as e:
                out, err = e.stdout, e.stderr
                raise
        except Exception as e:
            get_logger().exception(e)
            self._add_timeout(self.RENDER_ERROR_TIMEOUT_SEC)
            self._render_error()
            self._monitor_data_buf.clear()
        else:
            out, err = cp.stdout, cp.stderr

        if out:
            get_logger().info(out)
        if err:
            get_logger().error(err)

    def _enqueue_restart(self, _=None):
        self._enqueue(self._restart_service)

    def _render(self, msg: SocketMessage[ShocksInfo]):
        if self._state.is_waiting:
            if msg.data.running and msg.data.healthy:
                self._state.cancel_wait()
            else:
                icon = self._get_icon()
                if not self._show_lat:
                    self._render_result("", icon=icon)
                self._render_result("𐞄ᶸˢ𐞲", icon=icon)
                return

        self._render_result(
            self._format_result(msg.data),
            icon=self._get_icon(msg.data),
        )

    def _format_result(self, data: ShocksInfo) -> str:
        if not self._show_lat:
            return ""
        if not data.running:
            return "ᴼꟳꟳ"
        if not data.healthy:
            return "ERR"
        if not data.latency_s:
            return "---"
        if data.latency_s * 1000 >= self._latency_warning_threshold_ms:
            result = pt.format_auto_float(data.latency_s, 3, allow_exp_form=False) + "s"
        else:
            result = pt.format_time_ms(data.latency_s * 1e3)
        return result

    # noinspection PyMethodMayBeStatic
    def _get_icon_subtype(self, data: ShocksInfo = None) -> str:
        if not data:
            return "wait"
        if not data.running:
            return "disabled"
        if not data.healthy:
            return "failure"
        if (data.latency_s or 0) / 1000 >= self._latency_warning_threshold_ms:
            return "slow"
        return "up"

    def _get_icon(self, data: ShocksInfo = None) -> str:
        icon_subtype = self._get_icon_subtype(data)
        return self._icon_path_dynamic_tpl % icon_subtype
