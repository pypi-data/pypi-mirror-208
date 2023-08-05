# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

import click
import pytermor as pt

from ._base import CoreMonitor, MonitorCliCommand, CoreMonitorSettings, CoreMonitorConfig
from .._decorators import cli_pass_context, _catch_and_log_and_exit, _catch_and_print, cli_command
from ..exec_.list_dir import _Styles
from ...shared import SocketMessage
from ...shared.dto import NetworkTunnelInfo

OUTPUT_WIDTH = 1


@cli_command(
    name=__file__,
    cls=MonitorCliCommand,
    short_help="network tunnels count",
)
@cli_pass_context
@_catch_and_log_and_exit
@_catch_and_print
def invoker(ctx: click.Context, demo: bool, **kwargs):
    """
    ``
    """
    NetworkTunnelMonitor(ctx, demo, **kwargs)


class NetworkTunnelMonitor(CoreMonitor[NetworkTunnelInfo, CoreMonitorConfig]):
    def _init_settings(self, debug_mode: bool, force_cache: bool) -> CoreMonitorSettings[CoreMonitorConfig]:
        return CoreMonitorSettings[CoreMonitorConfig](
            socket_topic="network-tunnel",
            config=CoreMonitorConfig("monitor.network-tunnel", debug_mode, force_cache),
        )

    def get_output_width(self) -> int:
        return OUTPUT_WIDTH

    def _format_data_impl(self, msg: SocketMessage[NetworkTunnelInfo]) -> pt.Text:
        # label = 'T'
        val = str(msg.data.amount)

        val_st = _Styles.VALUE_PRIM_1
        if msg.data.amount == 0:
            val_st = _Styles.WARNING

        if len(val) > 1:
            val = '^'
        #   label = ''

        return pt.Text(
            pt.Fragment(val, val_st),
            # pt.Fragment(label, Styles.VALUE_LBL_5),
        )
