# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

from ._base import split_name
from .._decorators import cli_command, cli_argument, cli_option, _catch_and_log_and_exit
from ...shared import get_config, get_stdout


@cli_command(name="get")
@cli_argument("name")
@cli_option(
    "--boolean",
    is_flag=True,
    default=False,
    help='Cast the value to boolean "True" or "False".'
)
@_catch_and_log_and_exit
class GetCommand:
    """Display config variable value."""

    def __init__(self, name: str, boolean: bool):
        self._run(name, boolean)

    def _run(self, name: str, boolean: bool):
        section, option = split_name(name)
        if boolean:
            value = get_config().getboolean(section, option)
        else:
            value = get_config().get(section, option)
        get_stdout().echo(value)
