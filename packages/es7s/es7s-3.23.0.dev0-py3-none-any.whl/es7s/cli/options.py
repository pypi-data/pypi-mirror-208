# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import click

from ._base import (
    CliCommand,
    Context,
    HelpFormatter,
)
from ._base_opts_params import IntRange, OptionScope, CommonOption, EpilogPart
from ._decorators import cli_pass_context, _catch_and_log_and_exit, cli_command


class OptionsCliCommand(CliCommand):
    COMMON_OPTIONS = [
        CommonOption(
            param_decls=["-v", "--verbose"],
            count=True,
            type=IntRange(0, 3, clamp=True, show_range=False),
            default=0,
            help="Increase the amount of details: '-v' for more verbose info "
            "and exception stack traces, '-vv' for even more info, and '-vvv' for data "
            "dumps. The logging level also depends on this option; see the table below.",
        ),
        CommonOption(
            param_decls=["-q", "--quiet"],
            is_flag=True,
            default=False,
            help="Disables printing anything to a standard error stream, which includes: "
            "warnings, errors, debugging information and tracing. Note that silencing the "
            "application does not affect the logging system behaviour in the slightest.",
        ),
        CommonOption(
            param_decls=["-c", "--color"],
            is_flag=True,
            default=None,
            help="Explicitly enable output formatting using escape sequences.",
        ),
        CommonOption(
            param_decls=["-C", "--no-color"],
            is_flag=True,
            default=None,
            help="Explicitly disable output formatting.",
        ),
        CommonOption(
            param_decls=["--tmux"],
            is_flag=True,
            default=False,
            help="Transform output SGRs to tmux markup (respecting '-c|-C').",
        ),
        CommonOption(
            param_decls=["--trace"],
            is_flag=True,
            default=False,
            help="Alias for '-vvv'.",
        ),
        CommonOption(
            param_decls=["--default"],
            is_flag=True,
            default=False,
            help="Ignore user configuration file (if it exists), so that the "
            "default values are loaded.",
        ),
    ]

    EPILOG_INTRO = [
        EpilogPart(
            title="introduction",
            text="There are three different option scopes:",
        ),
        EpilogPart(
            "(1) Command-specific      (2) Group-specific       (3) Common",
        ),
        EpilogPart(
            "The first scope is referenced simply as *Options* and represents a set of "
            "local options for a defined command (e.g., '--recursive' for 'es7s exec "
            "list-dir' command)."
        ),
        EpilogPart(
            "The options in the second scope do not refer to a single command, but "
            "to a group of commands (e.g., '--demo' for 'es7s monitor' group) and belong "
            "to all the commands of that group."
        ),
        EpilogPart(
            "The third scope is application-wide -- all the options listed below can be "
            "added to any 'es7s' command whatsoever. Their descriptions were moved into "
            "a dedicated command to avoid useless repetitions and save some screen space."
        ),
        EpilogPart(
            title="Options order",
            text="Unlike the regular approach, common options (3) can be placed anywhere "
            "in the command and they `will` be correctly recognized, e.g.: "
            "\"'es7s -c exec -v list-dir'\" is the equivalent of \"'es7s exec list-dir -cv'\".",
        ),
        EpilogPart(
            "On the contrary, command-specific (1) and group-specific (2) options should "
            "always be placed *after* the command (as groups themselves are not actual commands "
            "and do not have arguments). To summarize:"
        ),
        EpilogPart("'es7s' @(3)@ 'group' @(3)@ 'command' @(1)@ @(2)@ @(3)@"),
    ]

    EPILOG = [
        EpilogPart(
            title="forcing/prohibiting the colors",
            text="/*(this part was written in the middle stage of es7s development, when the "
            "application ignored options in question in case no actual command was invoked, "
            "and the output consisted of help text only; later that was fixed, but I didn't "
            "find the strength to just purge these sections, as they can be still useful; "
            "therefore they were kept)*/",
        ),
        EpilogPart(
            "If neither of '--color' and '--no-color' is set, the output mode "
            "will be set depending on the output device (i.e. if the app "
            "sees a terminal, the colors will be enabled, and the opposite "
            "otherwise). This approach is common, but some applications do not implement "
            "options to forcefully enable or disable colors, and always rely on auto-"
            "detection instead. However, there are several ways to bypass this:",
        ),
        EpilogPart(
            "- To forcefully disable SGRs simply redirect or pipe the output stream "
            "somewhere, even a rudimentary 'cat' will work: 'es7s options | cat'. "
            "The application will see that the output is not an interactive terminal "
            'and thus will switch to "no formatting allowed" mode.',
        ),
        EpilogPart(
            "- Enabling SGRs by force is a bit trickier and requires some preparations, "
            "as well as Linux OS or similar. Install the 'unbuffer' small utility and "
            "launch the needed command like this: 'unbuffer es7s options'. It will work "
            "for almost any CLI application, not just for 'es7s', so personally I find "
            "it very handy. It doesn't matter if the output is redirected or not; the "
            "behaviour of the applications will be as if there *is* a terminal on the "
            "receiving side. To test it, run 'unbuffer es7s options | cat' -- the "
            "formatting should be present.",
        ),
        EpilogPart(
            "'unbuffer' homepage: https://core.tcl-lang.org/expect/home",
        ),
        EpilogPart(
            title="verbosity",
            text="""
╔══════╦════════════════╦═════════════════════╦═════════════════════╦══════╗\n\n
║ OPTS ║{ES7S_VERBOSITY}║    STDERR LEVEL     ║     SYSLOG LEVEL    ║ PBAR ║\n\n
╠══════╬════════════════╣═════════════════════╩═════════════════════╩══════╝\n\n
║ none ║ unset, empty   ║ ERR WRN             │ ERR WRN INF         │  YES │\n\n
║"-v"  ║ "1", "VERBOSE" ║ ERR WRN INF         │ ERR WRN INF DBG     │      │\n\n
║"-vv" ║ "2", "DEBUG"   ║ ERR WRN INF DBG     │ ERR WRN INF DBG TRC │      │\n\n
║"-vvv"║ "3", "TRACE"   ║ ERR WRN INF DBG TRC │ ERR WRN INF DBG TRC │  YES │\n\n
╚══════╩════════════════╝─────────────────────┴─────────────────────┴──────┘\n\n
╔══════════════════╦════════╦═════════╦═════════╦═════════╗\n\n
║ CMDLINE OPTIONS  ║::none::║  "-v"   ║  "-vv"  ║ "-vvv"  ║\n\n
║══════════════════║════════║═════════║═════════║═════════║\n\n
║ ENVIRONMENT VAR. ║ unset, ║  `1` or   ║ `2` or    ║ `3` or    ║\n\n
║  {ES7S_VERBOSITY}║ empty  ║ `VERBOSE` ║   `DEBUG` ║   `TRACE` ║\n\n
╚══════════════════╩════════╩═════════╩═════════╩═════════╝\n\n
    ║ STDERR LEVEL ║ WARN+    INFO+     DEBUG+    TRACE+  │\n\n
    ║ SYSLOG LEVEL ║ INFO+    DEBUG+    TRACE+    TRACE+  │\n\n
    ║ PROGRESS BAR ║ VISIBLE  HIDDEN    HIDDEN    VISIBLE │\n\n
    ║ DEBUG MARKUP ║ HIDDEN   ALLOWED   ALLOWED   ALLOWED │\n\n
    effects════════╝──────────────────────────────────────┘\n\n
    """,
        ),
    ]
    ENVIRONMENT_RO = [
        ("{ES7S_CLI}", "Contains path to CLI entrypoint of 'es7s' system."),
        ("",),
    ]
    ENVIRONMENT_WO = [
        (
            "{ES7S_VERBOSITY}",
            "Non-empty string determines detail level of the logs (for valid "
            "values see the table above). If the verbosity is set to max level, "
            "extended output of 'pytermor' formatting library is enabled as well (by "
            "setting @PYTERMOR_TRACE_RENDERS@). Works in [CLI], [DAEMON] and [GTK] "
            "domains, whereas '-v' or '--trace' options are recognized by CLI "
            "entrypoint only.",
        ),
        ("",),
        (
            "{ES7S_DAEMON_DEBUG}",
            "Non-empty string: ",
        ),
        *[
            ("", s)
            for s in (
                " - makes clients and daemon use different socket server address "
                "for IPC, which helps to avoid conflicts with installed and running "
                "system 'es7s' daemon instance; ",
                " - allows the python debugger to stay connected by keeping "
                "the daemon process attached.",
            )
        ],
        ("",),
        (
            "{ES7S_MONITOR_DEBUG}",
            "Non-empty string enables monitor output debugging markup. Has the "
            "same effect as <monitor.debug> config variable, but with higher priority, "
            "i.e. config variable will be ignored if there is an env variable. Is "
            "set by tmux, but can also be set manually, as a regular env var.",
        ),
        ("",),
        (
            "{ES7S_INDICATOR_DEBUG}",
            "Non-empty string enables indicator output debugging markup. Has the "
            "same effect as <indicator.debug> config variable, but with higher priority, "
            "i.e. config variable will be ignored if there is an env variable.",
        ),
        ("",),
    ]

    option_scopes: list[OptionScope] = [
        OptionScope.COMMON,
    ]

    def _include_common_options_epilog(self) -> bool:
        return False

    def _make_short_help(self, **kwargs) -> str:
        return kwargs.get("short_help")

    def format_usage(self, ctx: Context, formatter: HelpFormatter) -> None:
        pass

    def format_options(self, ctx: Context, formatter: HelpFormatter):
        pass

    def format_epilog(self, ctx: Context, formatter: HelpFormatter) -> None:
        self._format_epilog_parts(formatter, self.EPILOG_INTRO)
        formatter.write_paragraph()

        formatter.write_heading("Common options list", newline=True, colon=False)
        with formatter.indentation():
            formatter.write_dl([p.get_help_record(ctx) for p in self.COMMON_OPTIONS])

        self._format_epilog_parts(formatter, self.EPILOG)

        formatter.write_paragraph()
        formatter.write_heading("Environment (set by app for user)", newline=True, colon=False)
        with formatter.indentation():
            formatter.write_dl(self.ENVIRONMENT_RO)

        formatter.write_paragraph()
        formatter.write_heading("Environment (set by user)", newline=True, colon=False)
        with formatter.indentation():
            formatter.write_dl(self.ENVIRONMENT_WO)


@cli_command(
    name=__file__,
    cls=OptionsCliCommand,
    short_help="show shared command options",
)
@cli_pass_context
@_catch_and_log_and_exit
def options_command(ctx: click.Context, **kwargs):
    click.echo(ctx.get_help())
