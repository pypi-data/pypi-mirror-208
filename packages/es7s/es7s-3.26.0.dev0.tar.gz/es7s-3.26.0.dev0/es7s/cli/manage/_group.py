# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2021-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

import click

from . import update, install
from .._decorators import cli_pass_context, _catch_and_log_and_exit, cli_group


@cli_group(__file__)
@cli_pass_context
@_catch_and_log_and_exit
def group(ctx: click.Context, **kwargs):
    """Install/update es7s system."""


group.add_commands(
    install.InstallCommand,
    update.UpdateCommand,
)
