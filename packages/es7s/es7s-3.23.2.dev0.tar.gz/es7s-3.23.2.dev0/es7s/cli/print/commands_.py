# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import typing as t
from typing import cast

import click
import pytermor as pt

from es7s.shared import get_stdout, FrozenStyle
from .._base import (
    CliCommand,
    CliGroup,
    HelpFormatter,
    CliBaseCommand,
    HelpStyles,
)
from .._decorators import cli_pass_context, _catch_and_log_and_exit, cli_command


@cli_command(
    name=__file__,
    cls=CliCommand,
    short_help="tree of es7s commands",
)
@cli_pass_context
@_catch_and_log_and_exit
class PrintCommandsCommand:
    """
    Print es7s commands with descriptions as grouped (default) or plain list.
    """

    def __init__(self, ctx: click.Context, **kwargs):
        self._formatter = HelpFormatter()
        self.DEFAULT_CTYPE_CHAR = get_stdout().render("·", FrozenStyle(fg=pt.cv.BLUE, dim=True))
        self._run(ctx)

    def _run(self, ctx: click.Context):
        root_cmd = cast(CliGroup, ctx.find_root().command)

        self._formatter.write_dl([
            *filter(None, self._iterate(
                [*root_cmd.commands.values()], []
            ))
        ])

        self._formatter.write_paragraph()
        with self._formatter.indentation():
            self._formatter.write_dl(*[self._format_legend(root_cmd)])

        get_stdout().echo(self._formatter.getvalue())

    def _format_entry(self, cmd: CliBaseCommand, stack: list[str], st: pt.Style) -> tuple[str, str] | None:
        cname = " ".join(stack + [cmd.name])
        offset = len(stack) * 2 * " "
        ctype = cmd.get_command_type()
        ctype_str = self._formatter.format_command_type(ctype, default_char=self.DEFAULT_CTYPE_CHAR)
        cname_str = get_stdout().render(cname, st)
        left_col = offset + ctype_str + " " + cname_str

        right_col = ""
        if not isinstance(cmd, CliGroup):
            right_col = cmd.get_short_help_str()

        return left_col, right_col

    def _format_command(self, cmd: CliBaseCommand, stack: list[str]) -> tuple[str, str] | None:
        return self._format_entry(cmd, stack, HelpStyles.TEXT_COMMAND_NAME)

    def _format_group(self, cmd: CliBaseCommand, stack: list[str]) -> tuple[str, str] | None:
        return self._format_entry(cmd, stack, FrozenStyle(HelpStyles.TEXT_HEADING, bold=True))

    def _iterate(self, cmds: t.Iterable[CliBaseCommand], stack: list[str] = None):
        for cmd in sorted(cmds, key=lambda c: c.name):
            if not isinstance(cmd, CliGroup):
                yield self._format_command(cmd, stack)
            else:
                yield self._format_group(cmd, stack)
                yield from self._iterate(cmd.get_commands().values(), stack + [cmd.name])

    def _format_legend(self, root_cmd: CliGroup) -> tuple[str, str]:
        for ct in sorted(
            {*root_cmd.get_command_types(recursive=True)},
            key=lambda el: el.sorter,
        ):
            if not ct.char:
                continue
            if ct.is_default:
                continue
            yield self._formatter.format_command_type_desc(ct), ct.description.replace('%3s', '').replace('|', ' ')
