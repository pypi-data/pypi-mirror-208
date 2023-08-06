# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2021-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import io
import logging
import os
import re
import sys
import typing as t

import click
import pytermor as pt
import pytest
from click.testing import CliRunner

from es7s import APP_NAME
from es7s.cli import _entrypoint
from es7s.cli._base import CliGroup, CliBaseCommand
from es7s.shared import (
    init_logger,
    init_config,
    init_io,
    IoParams,
    destroy_io,
    destroy_logger,
    LoggerParams,
)


def rt_str(val) -> str | None:
    if isinstance(val, str):
        return str(val)
    if isinstance(val, click.Command):
        return repr(val)
    if isinstance(val, int):
        return f"0x{val:06x}"
    if isinstance(val, (list, tuple)):
        return "("+",".join(map(str, val))+")"
    if isinstance(val, dict):
        return f"(" + (" ".join((k + "=" + str(v)) for k, v in val.items())) + ")"
    return val


class IoInjector:
    """
    CliRunner swaps the original sys.stdout and sys.stderr with its own fake buffers in order to
    intercept and examine the output. In some cases (e.g., to debug) we want to intercept the
    output directly; furthermore, we want to set up logger and IO proxies in our tests using
    LoggerParams/IoParams instead of command line arguments. There is a few caveats:

    - We do not want to use cli._entrypoint.init_cli() because it reads sys.argv and initializes
      logger/IO with these options;

    - We cannot manually initialize logger/IO proxy BEFORE invoking CliRunner, because then the
      output will bypass our IO proxies and go right to the pytest runner's buffers.

    - We cannot manually initialize logger/IO proxy AFTER invoking CliRunner either,
      because actual entrypoint expects IO to be initialized right at the start.

    In order to implement the features mentioned above we need to (re)init IO:

        - AFTER the runner has been isolated the environment (i.e., replaced the streams), and

        - BEFORE an actual command invocation at the same time.

    Solution is to feed the runner a fake command wrapper (this class) as a command, which
    initializes IO in isolated environment and runs the actual command afterwards.
    """

    name = APP_NAME

    def __init__(
        self,
        logger_params: LoggerParams,
        io_params: IoParams,
        cli_runner: CliRunner,
        intercept: bool,
    ):
        self._logger_params = logger_params
        self._io_params = io_params
        self._cli_runner = cli_runner
        self._intercept = intercept

        self._io_stdout = None
        self._io_stderr = None
        self.stdout = None
        self.stderr = None

    def run_expect_ok(self, args: str | t.Sequence[str] | None):
        exit_code, stdout, stderr = self._run(args)
        assert not stderr, "Non-empty stderr"
        assert exit_code == 0, "Exit code > 0"

        return exit_code, stdout, stderr

    def _run(self, args: str | t.Sequence[str] | None):
        result = self._cli_runner.invoke(
            self, args
        )  # runner will call "<cmd>.main()", so we pass in "self"
        stdout = self.sanitize(self.stdout if self._intercept else result.stdout)
        stderr = self.sanitize(self.stderr if self._intercept else result.stderr)

        return result.exit_code, stdout, stderr

    def main(self, *args, **kwargs):
        os.environ.update({"ES7S_DOMAIN": "CLI_TEST"})
        init_logger(params=self._logger_params)

        if self._intercept:
            self._io_stdout = io.StringIO()
            self._io_stderr = io.StringIO()
        else:
            self._io_stdout = sys.stdout
            self._io_stderr = sys.stderr

        init_io(self._io_params, stdout=self._io_stdout, stderr=self._io_stderr)
        init_config()

        try:
            return _entrypoint.callback(*args, **kwargs)
        finally:
            if self._intercept:
                self._io_stdout.seek(0)
                self._io_stderr.seek(0)
                self.stdout = self._io_stdout.read()
                self.stderr = self._io_stderr.read()
                logging.debug(self.stdout)
                logging.debug(self.stderr)
                self._io_stdout.close()
                self._io_stderr.close()
            destroy_io()
            destroy_logger()

    @staticmethod
    def sanitize(s: str) -> str:
        return re.sub(r"(\s)\s+", r"\1", s)  # squash whitespace


@pytest.fixture(scope="function")
def cli_runner() -> CliRunner:
    yield CliRunner(mix_stderr=False)


@pytest.fixture(scope="function")  # , autouse=True)
def io_injector(request, cli_runner: CliRunner) -> IoInjector:
    logger_params = LoggerParams(out_syslog=False)
    io_params = IoParams()

    if logger_params_setup := request.node.get_closest_marker("logger_params"):
        logger_params = LoggerParams(**logger_params_setup.kwargs)
    if io_params_setup := request.node.get_closest_marker("io_params"):
        io_params = IoParams(**io_params_setup.kwargs)

    yield IoInjector(logger_params, io_params, cli_runner, intercept=False)


def _commands_names_flat_list(
    cmds: t.Iterable[CliBaseCommand] = (_entrypoint.callback,),
    stack: t.Tuple[str, ...] = (),
    only: t.Type[CliBaseCommand] = None,
) -> t.Iterable[t.Tuple[str, ...]]:
    for cmd in sorted(cmds, key=lambda c: c.name):
        if only is None or isinstance(cmd, only):
            yield *stack, cmd.name
        if isinstance(cmd, CliGroup):
            yield from _commands_names_flat_list(
                cmd.get_commands().values(), (*stack, cmd.name), only
            )


def group_list() -> t.Iterable[t.Tuple[str, ...]]:
    return _commands_names_flat_list(only=CliGroup)


def cmd_list() -> t.Tuple[str, ...]:
    return _commands_names_flat_list()  # noqa


class TestHelp:
    def test_entrypoint_help(self, io_injector):
        _, stdout, _ = io_injector.run_expect_ok("")
        expected_output = rf"Usage:\s*{APP_NAME}"
        assert re.search(expected_output, stdout, flags=re.MULTILINE), "Missing usage"

    @pytest.mark.parametrize("group", [*group_list()], ids=rt_str)
    def test_groups_help(self, io_injector, group):
        _, stdout, _ = io_injector.run_expect_ok([*group[1:], "--help"])
        expected_output = rf"Usage:\s*{' '.join(group)}"
        assert re.search(expected_output, stdout, flags=re.MULTILINE), "Missing usage"

    @pytest.mark.parametrize("command", [*cmd_list()], ids=rt_str)
    def test_commands_help(self, io_injector, command):
        _, stdout, _ = io_injector.run_expect_ok([*command[1:], "--help"])
        expected_output = rf"((Usage|Invoke directly instead):\s*{' '.join(command)})|Introduction"
        assert re.search(expected_output, stdout, flags=re.MULTILINE), "Missing usage"


class TestCommand:
    @pytest.mark.parametrize(
        "argstr, checks",
        [
            ["exec get-socket test-topic", "test-topic"],
            ["exec demo-progress-bar .", "Preparing"],
            ["exec hilight-num --demo", "http://localhost:8087/"],
            ["exec list-dir /", re.compile("([r-][w-][x-]){3}")],
            pytest.param("exec notify test", "", marks=[pytest.mark.skip()]),
            ["exec sun", re.compile("Dusk|Now")],
            ["exec wrap --demo", "text text"],
            ["help commands", "help commands"],
            ["print printscr", "UBUNTU PRINT SCREEN MODIFIERS"],
            ["print regex", "PYTHON REGULAR EXPRESSIONS"],
            ["print weather-icons", ("❄", "❄", "", "", "", re.compile("[ |]"))],
        ],
        ids=rt_str,
    )
    def test_command_invocation(
        self,
        io_injector,
        argstr: str,
        checks: str | re.Pattern | tuple[str | re.Pattern],
    ):
        _, stdout, _ = io_injector.run_expect_ok(argstr.split(" "))

        if isinstance(checks, (str, re.Pattern)):
            checks = (checks,)
        for check in checks:
            regex = check if isinstance(check, re.Pattern) else re.compile(check)
            assert regex.search(stdout), f"{regex} <- did not match stdout"


#     def test_stderr_transmits_error_by_default(self):
@pytest.mark.skip
class TestCliCommonOptions:
    @pytest.mark.io_params(color=True)
    def test_sgrs_in_output(self):
        result = CliRunner(mix_stderr=False).invoke(
            cli_streams.cmd,
            ["exec", "hilight-num", "--demo"],
        )
        cli_streams.stdout.seek(0)
        cli_streams.stderr.seek(0)

        assert len(cli_streams.stderr.read()) == 0, "Non-empty stderr"
        assert result.exit_code == 0, "Exit code > 0"
        assert pt.SGR_SEQ_REGEX.search(cli_streams.stdout.read()), "No SGRs found"

    @pytest.mark.io_params(color=False)
    def test_no_color_option_disables_sgrs(self):
        result = CliRunner(mix_stderr=False).invoke(
            cli_streams.cmd,
            ["exec", "hilight-num", "--demo"],
        )
        cli_streams.stdout.seek(0)
        cli_streams.stderr.seek(0)

        assert result.exit_code == 0, "Exit code > 0"
        assert len(cli_streams.stderr.read()) == 0, "Non-empty stderr"
        assert not pt.SGR_SEQ_REGEX.search(cli_streams.stdout.read()), "SGRs found"

    @pytest.mark.logger_params(verbosity=3)
    def test_verbose_option_works(self):
        result = CliRunner(mix_stderr=False).invoke(
            cli_streams.cmd,
            ["help", "commands"],
        )
        cli_streams.stderr.seek(0)

        assert result.exit_code == 0, "Exit code > 0"
        assert "Pre-click args" in cli_streams.stderr.read()

    @pytest.mark.logger_params(quiet=True, verbosity=3)
    def test_stderr_is_empty_with_quiet_flag(self):
        result = CliRunner(mix_stderr=False).invoke(
            cli_streams.cmd,
            ["help", "commands"],
        )
        cli_streams.stderr.seek(0)

        assert result.exit_code == 0, "Exit code > 0"
        assert len(cli_streams.stderr.read()) == 0, "Non-empty stderr"
