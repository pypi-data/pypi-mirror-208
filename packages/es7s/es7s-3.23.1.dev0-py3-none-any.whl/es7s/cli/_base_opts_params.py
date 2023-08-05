from __future__ import annotations

import abc
import enum
import typing as t
from abc import abstractmethod
from copy import copy
from dataclasses import dataclass

import click
import pytermor as pt

from es7s.shared import FrozenStyle

OPTION_DEFAULT = object()

# -----------------------------------------------------------------------------
# Parameter types


class IntRange(click.IntRange):
    def __init__(
        self,
        _min: t.Optional[float] = None,
        _max: t.Optional[float] = None,
        min_open: bool = False,
        max_open: bool = False,
        clamp: bool = False,
        show_range: bool = True,
    ):
        self._show_range = show_range
        super().__init__(_min, _max, min_open, max_open, clamp)

    def get_metavar(self, param: click.Parameter = None) -> t.Optional[str]:
        return "N"

    def _describe_range(self) -> str:
        if not self._show_range:
            return ""
        return super()._describe_range().replace("x", self.get_metavar())


class FloatRange(click.FloatRange):
    def __init__(
        self,
        _min: t.Optional[float] = None,
        _max: t.Optional[float] = None,
        min_open: bool = False,
        max_open: bool = False,
        clamp: bool = False,
        show_range: bool = True,
    ):
        self._show_range = show_range
        super().__init__(_min, _max, min_open, max_open, clamp)

    def get_metavar(self, param: click.Parameter = None) -> t.Optional[str]:
        return "X"

    def _describe_range(self) -> str:
        if not self._show_range:
            return ""
        return super()._describe_range().replace("x", self.get_metavar())


class EnumChoice(click.Choice):
    """
    Note: `show_choices` is ignored if param has custom metavar. That's because
    both metavar and choices in the left column of parameter list in --help mode
    look like shit and mess up the whole table. In case you need to set a metavar
    and to display choices at the same, add the latter into "help" message
    by setting `inline_choices` to True.
    """

    def __init__(self, impl: t.Any | enum.Enum, show_choices=True, inline_choices=False):
        self.__impl = impl
        self._show_choices = show_choices
        self.inline_choices = inline_choices
        super().__init__(choices=[item.value for item in impl], case_sensitive=False)

    def get_metavar(self, param: click.Parameter) -> str:
        if not self._show_choices:
            return ""
        return super().get_metavar(param)

    def get_choices(self) -> str:
        return " [" + "|".join(iter(self.__impl)) + "]"

    def convert(self, value, param, ctx):
        if value is None or isinstance(value, enum.Enum):
            return value

        converted_str = super().convert(value, param, ctx)
        return self.__impl(converted_str)


class OptionScope(str, enum.Enum):
    COMMON = "Common options"
    GROUP = "Group options"
    COMMAND = "Options"

    def __str__(self):
        return self.value


# -----------------------------------------------------------------------------
# Command options

class ScopedOption(click.Option, metaclass=abc.ABCMeta):
    @property
    @abstractmethod
    def scope(self) -> OptionScope:
        raise NotImplementedError

    def has_argument(self):
        if isinstance(self.type, click.IntRange):
            return not self.count
        return isinstance(
            self.type,
            (
                click.FloatRange,
                click.Choice,
                click.DateTime,
            ),
        )


class CommonOption(ScopedOption):
    scope = OptionScope.COMMON


class GroupOption(ScopedOption):
    scope = OptionScope.GROUP


class CommandOption(ScopedOption):
    scope = OptionScope.COMMAND


class DayMonthOption(CommandOption):
    _date_formats = ["%b-%d", "%m-%d", "%d-%b", "%d-%b", "%b%d", "%m%d", "%d%b", "%d%m"]

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("type", click.DateTime(self._date_formats))
        kwargs.setdefault("show_default", "current")
        kwargs.setdefault("metavar", "DD-MM")
        if kwargs.get("help") == OPTION_DEFAULT:
            kwargs.update({
                "help": 
                "Date of interest, where DD is a number between 1 and 31, and MM is "
                "either a number between 1 and 12 or month short name (first 3 characters). "
                "MM-DD format is also accepted. Hyphen can be omitted.",
            })
        super().__init__(*args, **kwargs)


# -----------------------------------------------------------------------------
# Command epilogues


@dataclass()
class EpilogPart:
    text: str
    title: str = None
    group: str = None


EPILOG_COMMAND_HELP = EpilogPart(
    "Run '%s' 'COMMAND' '--help' to get the COMMAND usage details (e.g. '%s' '%s' '--help').",
    group="run",
)
EPILOG_COMMON_OPTIONS = EpilogPart(
    "Run 'es7s options' to see common options details ('-v', '-q', '-c', '-C', '--tmux', "
    "'--default').",
    group="run",
)
EPILOG_ARGS_NOTE = EpilogPart(
    "Mandatory or optional arguments to long options are also mandatory or optional for any "
    "corresponding short options."
)


# -----------------------------------------------------------------------------
# Command types

@dataclass
class CommandType:
    char: str | None
    name: str
    sorter: int
    fmt: pt.FT = pt.NOOP_STYLE
    char_fmt: pt.FT = pt.NOOP_STYLE
    description: str = None
    is_default: bool = False

    def __eq__(self, other: CommandType) -> bool:
        if not isinstance(other, CommandType):
            return False
        return hash(self) == hash(other)

    def __hash__(self) -> int:
        return hash(f'{self.char or ""}{self.name}{self.fmt}{self.char_fmt}')

    def get_char_fmt(self) -> pt.Style:
        return FrozenStyle(pt.make_style(self.char_fmt or self.fmt), bold=True)

    def copy(self) -> t.Self:
        return copy(self)


CMDTYPE_GROUP = CommandType(
    "+",
    "group",
    sorter=10,
    fmt=pt.cv.HI_BLUE,
    char_fmt=pt.cv.YELLOW,
    description="This command %3s|contains|other commands.",
)
CMDTYPE_BUILTIN = CommandType(
    '⋅',
    "builtin",
    sorter=15,
    char_fmt=FrozenStyle(fg=pt.cv.BLUE, dim=True),
    description="This is a %3s|builtin|es7s/core component written in Python 3 (Gen.III).",
    is_default=True,
)
CMDTYPE_INTEGRATED = CommandType(
    "∙",
    "integrated",
    sorter=20,
    fmt=pt.cv.BLUE,
    description="This is an %3s|integrated legacy|component included in es7s/core, "
                "which can be launched separately, but requires es7s/commons "
                "shell library (Gen.I).",
)
CMDTYPE_EXTERNAL = CommandType(
    "▶",
    "standalone",
    sorter=28,
    fmt=pt.cv.CYAN,
    description="This is an external %3s|standalone component|which is not included in "
                "es7s/core, but is (usually) installed by it along-with the other "
                "es7s system parts.",
)
CMDTYPE_X11 = CommandType(
    "*",
    "X11",
    sorter=30,
    fmt=pt.cv.MAGENTA,
    description="This command requires %3s|X11 environment|for the normal work.",
)
CMDTYPE_DYNAMIC = CommandType(
    "~",
    "adaptive",
    sorter=40,
    fmt=pt.cv.GREEN,
    description="This command %3s|adjusts|the output depending on terminal size.",
)
