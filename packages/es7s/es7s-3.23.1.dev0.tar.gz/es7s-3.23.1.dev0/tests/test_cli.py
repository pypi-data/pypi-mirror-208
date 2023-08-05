# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2021-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import io
import os
import re
import typing as t
from dataclasses import dataclass

import click
import pytermor as pt
import pytest
from click.testing import CliRunner

from es7s import APP_NAME
from es7s.cli import _entrypoint as ep
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
    return str(val)


@dataclass
class CommandStreams:
    cmd: t.Callable[[click.Context, ...], click.BaseCommand] | click.BaseCommand
    stdout: t.IO
    stderr: t.IO


@pytest.fixture(scope="function")  # , autouse=True)
def cli_streams(request) -> CommandStreams:
    logger_params = LoggerParams()
    io_params = IoParams()

    if logger_params_setup := request.node.get_closest_marker("logger_params"):
        logger_params = LoggerParams(**logger_params_setup.kwargs)
    if io_params_setup := request.node.get_closest_marker("io_params"):
        io_params = IoParams(**io_params_setup.kwargs)

    os.environ.update({"ES7S_DOMAIN": "CLI_TEST"})
    init_logger(params=logger_params)

    stdout = io.StringIO()
    stderr = io.StringIO()
    init_io(io_params, stdout=stdout, stderr=stderr)
    init_config()
    yield CommandStreams(ep.callback, stdout, stderr)

    destroy_io()
    destroy_logger()


class TestHelp:
    def test_entrypoint_help(self, cli_streams: CommandStreams):
        result = CliRunner(mix_stderr=False).invoke(cli_streams.cmd, [])
        cli_streams.stdout.seek(0)
        cli_streams.stderr.seek(0)

        assert result.exit_code == 0, "Exit code > 0"
        assert len(cli_streams.stderr.read()) == 0, "Non-empty stderr"
        assert re.search(r"Usage:\s*"+APP_NAME, result.stdout, flags=re.MULTILINE), "Missing usage"

    @pytest.mark.parametrize("group", ep.all_groups, ids=rt_str)
    def test_groups_help(self, cli_streams: CommandStreams, group):
        result = CliRunner(mix_stderr=False).invoke(group, ["--help"])
        expected_output = rf"Usage:\s*{group.name}"
        cli_streams.stdout.seek(0)
        cli_streams.stderr.seek(0)

        assert result.exit_code == 0, "Exit code > 0"
        assert len(cli_streams.stderr.read()) == 0, "Non-empty stderr"
        assert re.search(expected_output, result.stdout, flags=re.MULTILINE), "Missing usage"

    @pytest.mark.parametrize("command", ep.all_commands, ids=rt_str)
    def test_commands_help(self, cli_streams: CommandStreams, command):
        result = CliRunner(mix_stderr=False).invoke(command, ["--help"])
        expected_output = rf"((Usage|Invoke directly instead):\s*{command.name})|Introduction"
        cli_streams.stdout.seek(0)
        cli_streams.stderr.seek(0)

        assert result.exit_code == 0, "Exit code > 0"
        assert len(cli_streams.stderr.read()) == 0, "Non-empty stderr"
        assert re.search(expected_output, result.stdout, flags=re.MULTILINE), "Missing usage"


class TestCommand:
    @pytest.mark.parametrize(
        "argstr, checks",
        [
            ["exec get-socket test-topic", "test-topic"],
            ["exec hilight-num --demo", "http://localhost:8087/"],
            ["exec list-dir /", re.compile("([r-][w-][x-]){3}")],
            pytest.param("exec notify test", "", marks=[pytest.mark.skip()]),
            ["exec sun", re.compile("Dusk|Now")],
            ["exec wrap --demo", "text text"],
            ["print commands", "print commands"],
            ["print printscr", "UBUNTU PRINT SCREEN MODIFIERS"],
            ["print regex", "PYTHON REGULAR EXPRESSIONS"],
            ["print weather-icons", ("❄", "❄", "", "", "", re.compile("[ |]"))],
        ],
        ids=rt_str,
    )
    def test_command_invocation(
        self,
        cli_streams: CommandStreams,
        argstr: str,
        checks: str | re.Pattern | tuple[str | re.Pattern],
    ):
        result = CliRunner().invoke(cli_streams.cmd, argstr.split(" "))
        cli_streams.stdout.seek(0)
        cli_streams.stderr.seek(0)

        assert result.exit_code == 0, "Exit code > 0"
        assert len(cli_streams.stderr.read()) == 0, "Non-empty stderr"
        stdout = cli_streams.stdout.read()

        if isinstance(checks, (str, re.Pattern)):
            checks = (checks,)
        for check in checks:
            regex = check if isinstance(check, re.Pattern) else re.compile(check)
            assert regex.search(stdout), f"{regex} <- did not match:\n{stdout}"


#     def test_stderr_transmits_error_by_default(self):
class TestCliCommonOptions:
    @pytest.mark.io_params(color=True)
    def test_sgrs_in_output(self, cli_streams: CommandStreams):
        result = CliRunner(mix_stderr=False).invoke(
            cli_streams.cmd,
            ["exec", "hilight-num", "--demo"],
        )
        cli_streams.stdout.seek(0)
        cli_streams.stderr.seek(0)

        assert result.exit_code == 0, "Exit code > 0"
        assert len(cli_streams.stderr.read()) == 0, "Non-empty stderr"
        assert pt.SGR_SEQ_REGEX.search(cli_streams.stdout.read()), "No SGRs found"

    @pytest.mark.io_params(color=False)
    def test_no_color_option_disables_sgrs(self, cli_streams: CommandStreams):
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
    def test_verbose_option_works(self, cli_streams: CommandStreams):
        result = CliRunner(mix_stderr=False).invoke(
            cli_streams.cmd,
            ["print", "commands"],
        )
        cli_streams.stderr.seek(0)

        assert result.exit_code == 0, "Exit code > 0"
        assert "Pre-click args" in cli_streams.stderr.read()

    @pytest.mark.logger_params(quiet=True, verbosity=3)
    def test_stderr_is_empty_with_quiet_flag(self, cli_streams: CommandStreams):
        result = CliRunner(mix_stderr=False).invoke(
            cli_streams.cmd,
            ["print", "commands"],
        )
        cli_streams.stderr.seek(0)

        assert result.exit_code == 0, "Exit code > 0"
        assert len(cli_streams.stderr.read()) == 0, "Non-empty stderr"
