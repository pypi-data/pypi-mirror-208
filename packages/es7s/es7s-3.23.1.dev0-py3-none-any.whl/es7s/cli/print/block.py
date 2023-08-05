# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from __future__ import annotations

from es7s.cli._base import CliCommand
from es7s.cli._decorators import _catch_and_log_and_exit, cli_command


@cli_command(
    name=__file__,
    cls=CliCommand,
    short_help="block drawings and other chars",
)
@_catch_and_log_and_exit
class PrintBlockCommand:
    """
    Print frequently used Unicode characters cheatsheet.
    """
    def __init__(self):
        from . import _block  # noqa
