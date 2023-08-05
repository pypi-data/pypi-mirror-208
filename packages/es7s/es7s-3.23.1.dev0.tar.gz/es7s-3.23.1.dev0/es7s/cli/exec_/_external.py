# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

from __future__ import annotations

import os

import click
import pytermor as pt

from es7s import APP_NAME
from .._base_opts_params import EpilogPart, CMDTYPE_EXTERNAL
from .._decorators import cli_pass_context, _catch_and_log_and_exit, cli_command, cli_argument
from ...shared import get_logger, format_attrs, get_color
from ...shared.config import get_app_config_yaml
from ...shared.path import RESOURCE_DIR, SHELL_COMMONS_FILE, USER_ES7S_BIN_DIR


@cli_pass_context
@_catch_and_log_and_exit
class ExternalCommand:
    """
    Launch the external component. PASSARGS are the arguments that will be
    passed to an external app. Long options can also be used, but make sure
    to prepend the "transit" options with "--" to help `click` library to
    distinguish them from its own options. Short options are known to be buggy,
    better just avoid using them on indirect invocations of standalone apps.
    """

    def __init__(self, ctx: click.Context, passargs: list[str] = None, **kwargs):
        if ctx.obj:
            self._run(*ctx.obj)
        else:
            self._run(ctx.command.name, passargs or [""])

    def _run(self, target_name: str, passargs: list[str]):
        import pkg_resources

        commons_path = pkg_resources.resource_filename(
            APP_NAME, os.path.join(RESOURCE_DIR, SHELL_COMMONS_FILE)
        )
        env = self._build_env(commons_path)

        try:
            self._spawn(target_name, passargs, env)
        except FileNotFoundError:
            get_logger().info(f'Executable "{target_name}" not found in PATH, trying local launch')
            target_path = pkg_resources.resource_filename(APP_NAME, os.path.join(RESOURCE_DIR, "bin", target_name))
            self._spawn(target_path, passargs, env)

    def _build_env(self, commons_path: str) -> dict:
        theme_seq = get_color().get_theme_color().to_sgr(bg=False)
        return {
            "ES7S_SHELL_COMMONS": commons_path,
            "ES7S_THEME_COLOR_SGR": ';'.join(map(str, theme_seq.params)),
            **os.environ,
            "PATH": self._build_path(),
        }

    def _build_path(self) -> str:
        current = os.environ.get("PATH", "").split(":")
        filtered = ":".join([
            # remove all deprecated es7s parts from PATH
            *filter(lambda s: "es7s" not in s, current),
            # add Gen.III path
            USER_ES7S_BIN_DIR,
        ])
        return filtered

    def _spawn(self, target_path: str, passarg: list[str], env: dict):
        get_logger().info(f"Launching: {target_path} {format_attrs(passarg)}")
        code = os.spawnvpe(os.P_WAIT, target_path, ["--", *passarg], env)  # os.environ)
        if code == 127:
            raise FileNotFoundError(f"Command not found: '{target_path}'")


EPILOG_PARTS = [
    EpilogPart(
        "This first command will result in 'es7s' command help text, while the second will result "
        "in 'watson's usage being displayed:",
        title="Invocation (generic):",
        group="ex1",
    ),
    EpilogPart("<  >", group="ex1"),
    EpilogPart("  (1) 'es7s exec watson --help'", group="ex1"),
    EpilogPart("  (2) 'es7s exec watson -- --help'", group="ex1"),
    EpilogPart("Another way to invoke an external component is to call it directly:", group="ex2"),
    EpilogPart("<  >", group="ex2"),
    EpilogPart("  (3) 'watson --help'", group="ex2"),
]


def make_external_commands():
    for name, desc in get_app_config_yaml("external-apps").items():
        cmd_fn = cli_command(
            name=name, type=CMDTYPE_EXTERNAL, short_help=desc, epilog=EPILOG_PARTS
        )
        arg_fn = cli_argument("passargs", type=str, nargs=-1, required=False)
        yield cmd_fn(arg_fn(ExternalCommand))
