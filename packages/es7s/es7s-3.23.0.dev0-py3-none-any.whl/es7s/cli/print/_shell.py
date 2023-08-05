# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import os
import typing as t

import click

from es7s.cli._base_opts_params import CMDTYPE_INTEGRATED
from es7s.shared import get_logger
from .._base import CliCommand, Context
from .._decorators import _catch_and_log_and_exit, cli_command
from ..exec_._external import ExternalCommand

SHELL_DIR_PATH = os.path.dirname(__file__)


class ShellCommandFactory:
    HELP_MAP = {
        "ruler": "Horizontal terminal char ruler.",
        "shell-param-exp": "Shell parameter expansion cheatsheet.",
    }

    def make_all(self) -> t.Iterable[click.Command]:
        for filename in os.listdir(SHELL_DIR_PATH):
            filepath = os.path.join(SHELL_DIR_PATH, filename)
            if not os.path.isfile(filepath) or os.path.splitext(filepath)[1] != ".sh":
                continue

            cmd = lambda ctx, filepath=filepath: ShellCommand(ctx, filepath)
            cmd = _catch_and_log_and_exit(cmd)
            cmd = click.pass_context(cmd)
            cmd = cli_command(
                name=filename,
                help=self.HELP_MAP.get(
                    os.path.splitext(filename)[0],
                    f"{filename} script",
                ),
                cls=CliCommand,
                type=CMDTYPE_INTEGRATED,
            )(cmd)
            yield cmd


class ShellCommand:
    def __init__(self, context: Context, filepath: str):
        get_logger().debug(f"Script filepath: '{filepath}'")
        context.obj = ["bash", [filepath]]
        context.invoke(ExternalCommand)
