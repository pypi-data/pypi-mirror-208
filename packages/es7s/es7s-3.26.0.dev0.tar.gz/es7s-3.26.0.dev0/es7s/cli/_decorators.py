# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

from __future__ import annotations

import sys
import typing as t
from functools import update_wrapper

import click
from click import Argument
from click.decorators import F, FC, _param_memo

from es7s.shared import get_logger, get_stdout, get_stderr
from es7s.shared.progress_bar import ProgressBar
from es7s.shared.threads import exit_gracefully
from ._base import CliGroup, CliCommand
from ._base_opts_params import EpilogPart, CommandOption, CMDTYPE_BUILTIN, CommandType, EnumChoice
from ._terminal_state import TerminalStateController


def _with_progress_bar(func: F) -> F:
    def wrapper(*args, **kwargs):
        pbar = ProgressBar(get_stdout(), get_logger(), kwargs.get("tstatectl", None))
        try:
            # pbar MUST be present in decorated constructor args:
            func(pbar, *args, **kwargs)
        finally:
            pbar.close()
        return func

    return update_wrapper(t.cast(F, wrapper), func)


def _preserve_terminal_state(func: F) -> F:
    def wrapper(*args, **kwargs):
        tstatectl = TerminalStateController()
        try:
            # tstatectl CAN be present in decorated constructor args:
            func(tstatectl=tstatectl, *args, **kwargs)
        finally:
            tstatectl.restore_state()
        return func

    return update_wrapper(t.cast(F, wrapper), func)


def _catch_and_log_and_exit(func: F) -> F:
    def wrapper(*args, **kwargs):
        logger = get_logger()
        try:
            logger.debug(f"Entering: '{func.__module__}'")
            func(*args, **kwargs)
        except Exception as e:
            logger.exception(e)
            exit_gracefully(1)
        except SystemExit as e:
            logger.debug(f"SystemExit: {e.args}")
        else:
            logger.debug(f"Leaving: '{func.__module__}'")
        return func

    return update_wrapper(t.cast(F, wrapper), func)


def _catch_and_print(func: F) -> F:
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            if stderr := get_stderr(require=False):
                stderr.echo("ERROR")
            else:
                sys.stderr.write("ERROR\n")
            raise
        return func

    return update_wrapper(t.cast(F, wrapper), func)


def cli_group(
    name: str,
    short_help: str = None,
    epilog: str | EpilogPart | list[str | EpilogPart] = None,
    **attrs: t.Any,
) -> CliGroup:
    if attrs.get("cls") is None:
        attrs["cls"] = CliGroup
    attrs.setdefault("short_help", short_help)
    attrs.setdefault("epilog", epilog)

    return t.cast(CliGroup, click.group(name, **attrs))


def cli_command(
    name: str,
    short_help: str = None,
    cls: type = CliCommand,
    type: CommandType = CMDTYPE_BUILTIN,
    **attrs: t.Any,
) -> CliCommand:
    attrs.setdefault("short_help", short_help)
    attrs.setdefault("type", type)

    return t.cast(CliCommand, click.command(name, cls, **attrs))


def cli_argument(*param_decls: str, **attrs: t.Any) -> t.Callable[[FC], FC]:
    def decorator(f: FC) -> FC:
        ArgumentClass = attrs.pop("cls", None) or Argument
        _param_memo(f, ArgumentClass(param_decls, **attrs))
        return f

    return decorator


def cli_option(
    *param_decls: str,
    help: str,
    cls=CommandOption,
    **attrs: t.Any,
) -> t.Callable[[FC], FC]:
    opt_type = attrs.get("type")
    if isinstance(opt_type, EnumChoice) and opt_type.inline_choices:
        help += opt_type.get_choices()
    attrs.setdefault("help", help)

    def decorator(f: FC) -> FC:
        option_attrs = attrs.copy()
        OptionClass = cls or option_attrs.pop("cls", CommandOption)
        _param_memo(f, OptionClass(param_decls, **option_attrs))
        return f

    return decorator


cli_pass_context = click.pass_context
