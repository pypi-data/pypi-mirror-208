# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

from .._decorators import cli_command, cli_option, _catch_and_log_and_exit
from ...shared import reset_config, get_stdout


@cli_command(name="reset", short_help="Reset config values to default")
@cli_option(
    "-p",
    "--prune",
    is_flag=True,
    default=False,
    help="Silently overwrite original config, do not make a backup."
)
@_catch_and_log_and_exit
class ResetCommand:
    """
    Make a backup and replace current user config with the default one.
    The original file is preliminarily renamed to "<filename>.bak".
    """

    def __init__(self, prune: bool):
        self._run(prune)

    def _run(self, prune: bool):
        reset_config(backup=not prune)
        get_stdout().echo("Config was reset to default")
