# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2021-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

import click

from . import (
    weather,
    docker,
    fan_speed,
    memory,
    battery,
    combined,
    network_latency,
    cpu_freq,
    timestamp,
    cpu_load,
    cpu_load_avg,
    network_tunnel,
    temperature,
    datetime,
    disk_usage,
    network_country,
)
from .._decorators import cli_pass_context, _catch_and_log_and_exit, cli_group


@cli_group(__file__, short_help="run system monitor")
@cli_pass_context
@_catch_and_log_and_exit
def group(ctx: click.Context, **kwargs):
    """
    Launch one of es7s system monitors, or indicators. Mostly
    used by tmux.
    """


group.add_commands(
    combined.CombinedMonitor,
    battery.invoker,
    datetime.invoker,
    docker.invoker,
    cpu_load.invoker,
    cpu_load_avg.invoker,
    cpu_freq.invoker,
    disk_usage.invoker,
    fan_speed.invoker,
    memory.invoker,
    network_country.invoker,
    network_latency.invoker,
    network_tunnel.invoker,
    timestamp.invoker,
    temperature.invoker,
    weather.invoker,
)
