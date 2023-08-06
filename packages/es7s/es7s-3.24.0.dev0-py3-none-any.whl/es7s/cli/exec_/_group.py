# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from __future__ import annotations

import click

from . import (
    get_socket,
    hilight_num,
    list_dir,
    notify,
    sun,
    wrap,
    edit_image,
    switch_wspace,
    _external,
    demo_progress_bar,
)
from .._decorators import cli_pass_context, _catch_and_log_and_exit, cli_group


@cli_group(__file__, short_help="run an embed or external component")
@cli_pass_context
@_catch_and_log_and_exit
def group(ctx: click.Context, **kwargs):
    """
    Commands that invoke one of es7s subsystems that has been made available
    for standalone manual launching via CLI.
    """


group.add_commands(
    get_socket.GetSocketCommand,
    hilight_num.HighlightNumbersCommand,
    demo_progress_bar.DemoProgressBarCommand,
    edit_image.EditImageCommand,
    list_dir.ListDirCommand,
    notify.NotifyCommand,
    sun.SunCommand,
    switch_wspace.SwitchWorkspaceCommand,
    wrap.WrapCommand,
    *_external.make_external_commands(),  # @TODO можно выпилить yaml для ускорения загрузки
)
