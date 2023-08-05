# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

from ._base import split_name
from .._decorators import cli_command, cli_argument, _catch_and_log_and_exit
from ...shared import get_config, get_stdout, save_config


@cli_command(name="set")
@cli_argument("name")
@cli_argument("value")
@_catch_and_log_and_exit
class SetCommand:
    """Set config variable value."""

    def __init__(self, name: str, value: str):
        self._run(name, value)

    def _run(self, name: str, value: str):
        section, option = split_name(name)
        get_config().set(section, option, value)
        save_config()
        get_stdout().echo("Done")
