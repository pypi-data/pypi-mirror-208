# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from __future__ import annotations

import click

from . import (
    options,
    commands_,
)
from .._decorators import cli_pass_context, _catch_and_log_and_exit, cli_group


@cli_group(__file__, short_help="display es7s system help topics")
@cli_pass_context
@_catch_and_log_and_exit
def group(ctx: click.Context, **kwargs):
    """
    Commands that invoke one of es7s subsystems that has been made available
    for standalone manual launching via CLI.
    """


group.add_commands(
    commands_.PrintCommandsCommand,
    options.options_command,
)
