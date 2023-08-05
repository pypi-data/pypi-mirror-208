# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2021-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

import click

from . import regex, weather_icons, _static, _shell, commands_, block
from .keys._group import group as keys_group
from .._decorators import cli_pass_context, _catch_and_log_and_exit, cli_group


@cli_group(__file__, short_help="various data in a terminal-friendly format")
@cli_pass_context
@_catch_and_log_and_exit
def group(ctx: click.Context, **kwargs):
    """Display various data in a form (fundamentally) designed for command line interface."""


group.add_commands(
    keys_group,
    regex.RegexPrinter,
    weather_icons.WeatherIconsPrinter,
    commands_.PrintCommandsCommand,
    block.PrintBlockCommand,
    *_static.StaticCommandFactory().make_all(),
    *_shell.ShellCommandFactory().make_all(),
)
