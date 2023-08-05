# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

import re

import click
import pytermor as pt

from es7s.shared import get_default_config, get_config, get_stdout, FrozenStyle
from .._decorators import cli_command, _catch_and_log_and_exit


@cli_command(name="list")
@click.option(
    "--default",
    is_flag=True,
    default=False,
    help="List default variables and values instead of user's. Actually this is "
         "not a self-determined option, rather a reference to common (or global) "
         "option with the same name and effect, "
         "which is making the config loader ignore user config file and read only "
         "the default one. In other words, this option can be used with each and "
         "every command.",
)
@_catch_and_log_and_exit
class ListCommand:
    """Display user [by default] config variables with values."""

    HEADER_STYLE = FrozenStyle(fg=pt.cv.YELLOW)
    OPT_NAME_STYLE = FrozenStyle(fg=pt.cv.GREEN)
    OPT_VALUE_STYLE = FrozenStyle(bold=True)

    def __init__(self, default: bool):
        self._run(default)

    def _run(self, default: bool):
        config = get_default_config() if default else get_config()
        stdout = get_stdout()
        for idx, section in enumerate(config.sections()):
            if idx > 0:
                stdout.echo()
            stdout.echo_rendered(f"[{section}]", self.HEADER_STYLE)
            for option in config.options(section):
                option_fmtd = stdout.render(option, self.OPT_NAME_STYLE)
                value_fmtd = self._render_value(config.get(section, option))
                stdout.echo_rendered(option_fmtd + " = " + value_fmtd)

    def _render_value(self, val: str) -> str:
        val = re.sub('\n+', '\n    ', val)
        return get_stdout().render(val, self.OPT_VALUE_STYLE)
