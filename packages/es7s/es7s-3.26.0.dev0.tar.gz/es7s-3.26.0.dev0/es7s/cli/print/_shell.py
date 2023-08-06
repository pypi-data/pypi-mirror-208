# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import os
import typing as t

import click

from es7s.cli._base_opts_params import CMDTYPE_INTEGRATED, CMDTRAIT_ADAPTIVE
from es7s.shared import get_logger
from .._base import CliCommand, Context
from .._decorators import _catch_and_log_and_exit, cli_command
from ..exec_._external import ExternalCommand

SHELL_DIR_PATH = os.path.dirname(__file__)


class ShellCommandFactory:
    HELP_MAP = {
        "colors": ("xterm-16, xterm-256 and rgb color tables",),
        "ruler": ("Horizontal terminal char ruler.", CMDTRAIT_ADAPTIVE),
        "shell-param-exp": ("Shell parameter expansion cheatsheet.",),
    }

    def make_all(self) -> t.Iterable[click.Command]:
        for filename in os.listdir(SHELL_DIR_PATH):
            filepath = os.path.join(SHELL_DIR_PATH, filename)
            if not os.path.isfile(filepath) or os.path.splitext(filepath)[1] != ".sh":
                continue

            cmd = lambda ctx, filepath=filepath: ShellCommand(ctx, filepath)
            cmd = _catch_and_log_and_exit(cmd)
            cmd = click.pass_context(cmd)
            attributes = self.HELP_MAP.get(os.path.splitext(filename)[0], (f"{filename} script",))
            cmd = cli_command(
                name=filename,
                help=attributes[0],
                cls=CliCommand,
                type=CMDTYPE_INTEGRATED,
                traits=[*attributes[1:]],
                ignore_unknown_options=True,
                allow_extra_args=True,
            )(cmd)
            yield cmd


class ShellCommand:
    def __init__(self, context: Context, filepath: str):
        get_logger().debug(f"Script filepath: '{filepath}'")
        context.obj = ["bash", [filepath, *context.args]]
        context.ignore_unknown_options = True
        context.invoke(ExternalCommand)
