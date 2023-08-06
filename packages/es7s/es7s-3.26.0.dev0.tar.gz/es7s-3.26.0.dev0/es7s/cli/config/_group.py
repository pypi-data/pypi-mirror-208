# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2021-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

import click

from . import (
    get,
    list,
    reset,
    set,
    edit,
)
from .._decorators import cli_pass_context, _catch_and_log_and_exit, cli_group


@cli_group(name=__file__)
@cli_pass_context
@_catch_and_log_and_exit
def group(ctx: click.Context, **kwargs):
    """Show/edit es7s preferences."""


group.add_commands(
    list.ListCommand,
    reset.ResetCommand,
    get.GetCommand,
    set.SetCommand,
    edit.EditCommand,
)
