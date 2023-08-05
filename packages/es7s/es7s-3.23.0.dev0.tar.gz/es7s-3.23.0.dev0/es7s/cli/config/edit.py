# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

import os

from es7s.shared.sub import run_detached
from .._decorators import cli_command, _catch_and_log_and_exit
from ...shared import get_user_config_filepath, get_stdout, get_logger


@cli_command(name="edit")
@_catch_and_log_and_exit
class EditCommand:
    """Open current user config in text editor."""

    def __init__(self):
        self._run()

    def _run(self):
        logger = get_logger()

        user_config_filepath = get_user_config_filepath()
        editor = os.getenv("EDITOR", "xdg-open")
        logger.debug(f"Determining the editor executable: '{editor}'")

        run_detached(f"{editor} {user_config_filepath}")
        get_stdout().echo("Done")
