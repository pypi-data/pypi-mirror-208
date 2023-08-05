# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from __future__ import annotations

import inspect
import re
import typing as t
from contextlib import contextmanager
from dataclasses import dataclass
from os.path import basename, dirname, splitext
from typing import cast, overload

import Levenshtein
import click
import pytermor as pt

from es7s import APP_NAME
from es7s.shared import (
    get_logger,
    get_stdout,
    format_attrs,
    Styles,
    FrozenStyle,
)
from ._base_opts_params import (
    OptionScope,
    ScopedOption,
    EpilogPart,
    EPILOG_COMMAND_HELP,
    EPILOG_COMMON_OPTIONS,
    EPILOG_ARGS_NOTE,
    CommandType,
    CMDTYPE_BUILTIN,
    CMDTYPE_GROUP,
)


@dataclass(frozen=True)
class Examples:
    title: str
    content: t.Sequence[str]

    def __bool__(self) -> bool:
        return len(self.content) > 0


# fmt: off
class HelpStyles(Styles):
    TEXT_HEADING = FrozenStyle(fg=pt.cv.YELLOW, bold=True)          # SYNOPSIS      |   | explicit manual usage only      # noqa
    TEXT_COMMAND_NAME = FrozenStyle(fg=pt.cv.BLUE)                  # es7s exec     |   | auto-detection                  # noqa
    TEXT_OPTION_DEFAULT = FrozenStyle(fg=pt.cv.HI_YELLOW)           # [default: 1]  |[ ]| requires wrapping in [ ]        # noqa
    TEXT_LITERAL = FrozenStyle(bold=True)                           # 'ls | cat'    | ' | non-es7s commands (punctuation) # noqa
    TEXT_LITERAL_WORDS = FrozenStyle(underlined=True)               # 'ls | cat'    | ' | non-es7s commands (words)       # noqa
    TEXT_EXAMPLE = FrozenStyle(fg=pt.cv.CYAN, bg='full-black')      # ` 4 11`       | ` | output example                  # noqa
    TEXT_ENV_VAR = FrozenStyle(fg=pt.cv.GREEN, bold=True)           # {ES7S_LE_VAR} |{ }| environment variable name       # noqa
    TEXT_ABOMINATION = FrozenStyle(
        pt.Style(bg=pt.cv.BLUE).autopick_fg())           # ::NOTE::      |:: | needs to be wrapped in ::       # noqa
    TEXT_DEPENDENCY = FrozenStyle(fg=pt.cv.RED, underlined=True)    # ++REQ++       |++ | ++required dependency++         # noqa
    TEXT_INLINE_CONFIG_VAR = FrozenStyle(fg=pt.cv.MAGENTA)          # <section.opt> |< >| config variable name            # noqa
    TEXT_ALTER_MODE = FrozenStyle(italic=True)                      # ^ALT MODE^    |^ ^| alt monitor mode                # noqa
    TEXT_COMMENT = FrozenStyle(fg=pt.cv.GRAY)                       # // COMMENT    |// | till end of the line            # noqa
    TEXT_ACCENT = FrozenStyle(bold=True)                            # *important*   | * | needs to be wrapped in *        # noqa
                                                                      #  '--option' | ' | auto-detection if wrapped in '  # noqa
                                                                      #  "--option" | " | " -> space instead of removing  # noqa
# fmt: on


class HelpFormatter(click.HelpFormatter):
    OPT_DEFAULT_REGEX = re.compile(r"(default:\s*)(.+?)([];])|(\[[\w\s]+)(default)(])")
    OPT_REF_REGEX = re.compile(r"'(\n\s*)?(--?[\w-]+)'")
    OPT_REF_FIX_REGEX = re.compile(r'"(\n\s*)?(--?[\w-]+)"')  # < @TODO join with regular
    ACCENT_REGEX = re.compile(r"(^|)?\*([\w!/-]+?)\*")
    LITERAL_REGEX = re.compile(r"'(\n\s*)?([\w/ \n|-]+?)'")
    EXAMPLE_REGEX = re.compile(r"`(\n\s*)?(.+?)`")
    INLINE_CONFIG_VAR_REGEX = re.compile(r"<(\n\s*)?([\w\s.-]+?)>")
    ENV_VAR_REGEX = re.compile(r"\{(\n\s*)?([\w.-]+?)}")  # @FIXME join with other wrappers?
    INLINE_ENV_VAR_REGEX = re.compile(r"@([()\w._-]+?)@")  # @FIXME join with other wrappers?
    ABOMINATION_REGEX = re.compile(r"::([\w./-]+?:*)::")
    DEPENDENCY_REGEX = re.compile(r"\+\+([\w./-]+?:*)\+\+")
    ALTER_MODE_REGEX = re.compile(r"\^([\w .!/-]+?)\^")
    COMMENT_REGEX = re.compile(r"(\s//\s?)(.+)($)")
    COMMENT_BLOCK_REGEX = re.compile(r"/\*()(.+)()\*/", flags=re.DOTALL)

    def __init__(
        self,
        indent_increment: int = 2,
        width: t.Optional[int] = None,
        max_width: t.Optional[int] = None,
    ):
        width = pt.get_preferable_wrap_width(False)
        super().__init__(indent_increment, width, max_width)

        self.help_filters: t.List[pt.StringReplacer] = [
            pt.StringReplacer(self.OPT_DEFAULT_REGEX, self.format_option_default),
            pt.StringReplacer(self.OPT_REF_REGEX, self.format_accent),
            pt.StringReplacer(self.OPT_REF_FIX_REGEX, self.format_accent_fixed),
            pt.StringReplacer(self.ACCENT_REGEX, self.format_accent),
            pt.StringReplacer(self.LITERAL_REGEX, self.format_literal),
            pt.StringReplacer(self.EXAMPLE_REGEX, self.format_example),
            pt.StringReplacer(self.INLINE_CONFIG_VAR_REGEX, self.format_inline_config_var),
            pt.StringReplacer(self.ENV_VAR_REGEX, self.format_env_var),
            pt.StringReplacer(self.INLINE_ENV_VAR_REGEX, self.format_inline_env_var),
            pt.StringReplacer(self.ABOMINATION_REGEX, self.format_abomination),
            pt.StringReplacer(self.DEPENDENCY_REGEX, self.format_dependency),
            pt.StringReplacer(self.ALTER_MODE_REGEX, self.format_alter_mode),
            pt.StringReplacer(self.COMMENT_REGEX, self.format_comment),
            pt.StringReplacer(self.COMMENT_BLOCK_REGEX, self.format_comment),
        ]

        self.command_names = [APP_NAME]
        if (ctx := click.get_current_context(True)) is None:
            return
        self.command_names = self._find_all_command_names(ctx.find_root().command)

    def _find_all_command_names(self, command: click.Command) -> set[str]:
        names = set()
        names.add(command.name)
        if hasattr(command, "commands") and isinstance(command.commands, dict):
            for nested_command in command.commands.values():
                names = names.union(self._find_all_command_names(nested_command))
        return names

    def format_option_default(self, m: re.Match) -> str:
        return (
            (m.group(1) or m.group(4))
            + get_stdout().render(m.group(2) or m.group(5), HelpStyles.TEXT_OPTION_DEFAULT)
            + (m.group(3) or m.group(6))
        )

    def format_command_name(self, arg: re.Match | str) -> str:
        if isinstance(arg, re.Match):
            arg = arg.group(1)
        return get_stdout().render(arg, HelpStyles.TEXT_COMMAND_NAME)

    def format_command_type(self, ct: CommandType, default_char=" ") -> str:
        if not ct.char:
            return default_char
        return get_stdout().render(ct.char, ct.get_char_fmt())

    def format_command_type_desc(self, ct: CommandType) -> str:
        return "[" + self.format_command_type(ct) + "] " + ct.name

    @overload
    def format_command_name_and_type(self, ct: CommandType, cmd_name: str) -> str:
        ...

    @overload
    def format_command_name_and_type(self, cmd: CliBaseCommand) -> str:
        ...

    def format_command_name_and_type(self, *args) -> str:
        if len(args) == 1:
            cmd = args[0]
            return self.format_command_name_and_type(cmd.get_command_type(), cmd.name)
        ct, cmd_name = args
        return self.format_command_type(ct) + " " + self.format_command_name(cmd_name)

    def format_accent(self, m: re.Match) -> str:
        return get_stdout().render((m.group(1) or "") + m.group(2), HelpStyles.TEXT_ACCENT)

    def format_accent_fixed(self, m: re.Match) -> str:
        return get_stdout().render(
            " " + (m.group(1) or "") + m.group(2) + " ", HelpStyles.TEXT_ACCENT
        )

    def format_example(self, m: re.Match) -> str:
        return get_stdout().render((m.group(1) or "") + m.group(2), HelpStyles.TEXT_EXAMPLE)

    def format_inline_config_var(self, m: re.Match) -> str:
        result = m.group(1) or ""
        return result + ".".join(
            get_stdout().render(name, HelpStyles.TEXT_INLINE_CONFIG_VAR)
            for name in re.split(r"\.\s*", m.group(2))
        )

    def format_env_var(self, m: re.Match):
        return get_stdout().render(
            (m.group(1) or "") + " " + m.group(2) + " ", HelpStyles.TEXT_ENV_VAR
        )

    def format_inline_env_var(self, m: re.Match):
        return get_stdout().render(m.group(1), HelpStyles.TEXT_ENV_VAR)

    def format_abomination(self, m: re.Match):
        return " " + get_stdout().render(" " + m.group(1) + " ", HelpStyles.TEXT_ABOMINATION) + " "

    def format_dependency(self, m: re.Match):
        return get_stdout().render(m.group(1), HelpStyles.TEXT_DEPENDENCY)

    def format_alter_mode(self, m: re.Match):
        return get_stdout().render(m.group(1), HelpStyles.TEXT_ALTER_MODE) + "  "

    def format_comment(self, m: re.Match):
        return (
            "." * len(m.group(1))
            + get_stdout().render(m.group(2), HelpStyles.TEXT_COMMENT)
            + ":" * len(m.group(3))
        )

    def format_heading(self, s: str) -> str:
        return get_stdout().render(s, HelpStyles.TEXT_HEADING)

    def format_literal(self, sm: re.Match) -> str:
        text_literal_is_present = False
        word_count = 0

        def replace_literal(wm: re.Match) -> str:
            nonlocal text_literal_is_present, word_count
            word_count += 1
            word = wm.group()
            if len(word) < 2:
                text_literal_is_present = True
                style = HelpStyles.TEXT_LITERAL
            elif word in self.command_names or word.startswith(APP_NAME):
                style = HelpStyles.TEXT_COMMAND_NAME
            elif word.startswith("-"):
                style = HelpStyles.TEXT_ACCENT
            else:
                text_literal_is_present = True
                style = HelpStyles.TEXT_LITERAL_WORDS
            return get_stdout().render(word, style)

        replaced = re.sub(r"(\S+)", replace_literal, (sm.group(1) or "") + sm.group(2))
        if text_literal_is_present and word_count > 1:
            replaced = f"'{replaced}'"
        return replaced

    @contextmanager
    def section(self, name: str | None) -> t.Iterator[None]:
        # modified version of parent implementation; could not inject otherwise
        # changes: `name` is nullable now; do not write heading if `name` is empty
        self.write_paragraph()
        if name:
            self.write_heading(name)
        self.indent()
        try:
            yield
        finally:
            self.dedent()

    def write_heading(self, heading: str, newline: bool = False, colon: bool = True):
        heading = get_stdout().render(heading + (colon and ":" or ""), HelpStyles.TEXT_HEADING)
        self.write(f"{'':>{self.current_indent}}{heading}")
        self.write_paragraph()
        if newline:
            self.write_paragraph()

    def write_text(self, text: str) -> None:
        self.write(
            pt.wrap_sgr(
                text,
                self.width,
                indent_first=self.current_indent,
                indent_subseq=self.current_indent,
            )
        )

    def write_squashed_text(self, string: str):
        wrapped_text = pt.wrap_sgr(
            string,
            self.width,
            indent_first=self.current_indent,
            indent_subseq=self.current_indent,
        )
        self.write(wrapped_text.replace("\n\n", "\n"))
        self.write("\n")

    def write(self, string: str) -> None:
        stripped = string.strip()
        if stripped in self.command_names:
            string = get_stdout().render(string, HelpStyles.TEXT_COMMAND_NAME)
        if stripped.startswith(APP_NAME):
            string = re.sub("([a-z0-9_-]+)", lambda m: self.format_command_name(m), string, 3)
        else:
            string = pt.utilstr.apply_filters(string, *self.help_filters)
        self.buffer.append(string)


class Context(click.Context):
    formatter_class = HelpFormatter

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.failed = False
        self.color = get_stdout().color

    def fail(self, message: str):
        self.failed = True
        super().fail(message)


class CliBaseCommand(click.Command):
    context_class = Context

    def __init__(self, name, **kwargs):
        kwargs.setdefault("type", CMDTYPE_BUILTIN)
        self._command_type: CommandType = kwargs.pop("type")

        base_name = name or kwargs.get("name")
        if ".py" in base_name:
            base_name = splitext(basename(base_name))
            self._file_name_parts = base_name[0].lstrip("_").split("_")
        else:
            self._file_name_parts = [base_name]

        super().__init__(name, **kwargs)

    def get_command_type(self) -> CommandType:
        return self._command_type

    def parse_args(self, ctx: Context, args: t.List[str]) -> t.List[str]:
        get_logger().debug(f"Pre-click args:  {format_attrs(args)}")
        parsed_args = super().parse_args(ctx, args)
        return parsed_args

    def invoke(self, ctx: Context) -> t.Any:
        get_logger().debug(f"Post-click args: {format_attrs(ctx.params)}")
        try:
            return super().invoke(ctx)
        except click.ClickException as e:
            ctx.failed = True
            self.show_error(ctx, e)

    def show_error(self, ctx: Context, e: click.ClickException):
        logger = get_logger()
        logger.error(e.format_message())
        if logger.quiet:
            return

        hint = ""
        if ctx.command.get_help_option(ctx):
            hint = f"\nTry '{ctx.command_path} {ctx.help_option_names[0]}' for help."
        get_stdout().echo(f"{ctx.get_usage()}\n{hint}")

    def _make_command_name(self, orig_name: str) -> str:
        dir_name = basename(dirname(orig_name))
        filename_parts = splitext(basename(orig_name))[0].rstrip("_").split("_")
        if filename_parts[0] == "":  # because of '_group' -> ['', 'group']
            filename_parts = [dir_name.rstrip("_")]  # 'exec_' -> 'exec'
        return "-".join(filename_parts)

    def _make_short_help(self, **kwargs) -> str:
        help_str = kwargs.get("help")
        if not help_str:
            if logger := get_logger(require=False):
                logger.warning(f"Missing help for '{kwargs.get('name')}' command")
            help_str = "..."

        short_help = kwargs.get("short_help")
        short_help_auto = help_str.lower().removesuffix(".")
        if isinstance(short_help, t.Callable):
            return short_help(short_help_auto)
        elif short_help:
            return short_help
        return short_help_auto

    def format_own_command_type(self, ctx: Context, formatter: HelpFormatter):
        # if (ct := self.get_command_type()).is_default:
        #    return
        ct = self.get_command_type()
        if "%3s" not in ct.description:
            return

        with formatter.indentation():
            st = FrozenStyle(
                pt.make_style(ct.get_char_fmt()),
                bg=0xFFFFFF,
                dim=True,
                bold=True,
                inversed=True,
            )
            ct_icon = get_stdout().render(f'{ct.char or " ":^3s}', st)
            if ct.description.count("|") == 2:
                left, hightlight, right = ct.description.split("|", 2)
                description = (
                    left + get_stdout().render(" " + hightlight + " ", ct.get_char_fmt()) + right
                )
            else:
                description = ct.description

            formatter.write_paragraph()
            formatter.write_text(description % ct_icon)

    def format_common_options(self, ctx: Context, formatter: HelpFormatter, add_header: bool):
        if self._include_common_options_epilog():
            with formatter.section("Options" if add_header else ""):
                formatter.write_text(EPILOG_COMMON_OPTIONS.text)

    def format_epilog(self, ctx: Context, formatter: HelpFormatter) -> None:
        epilog_parts = []

        if self.epilog:
            if not isinstance(self.epilog, list):
                self.epilog = [self.epilog]
            epilog_parts.extend(self.epilog)

        if isinstance(self, click.Group):
            epilog_parts.append(EPILOG_COMMON_OPTIONS)

            non_group_subcmds = sorted(
                [
                    cmd
                    for cmd in self.commands.values()
                    if not isinstance(cmd, CliGroup) and not cmd.name == "options"
                ],
                key=lambda v: v.name,
            )

            example_cmd = [*self.commands.values()][0]
            if len(non_group_subcmds):
                example_cmd = non_group_subcmds[0]

            epilog_parts.append(
                EpilogPart(
                    EPILOG_COMMAND_HELP.text
                    % (ctx.command_path, ctx.command_path, example_cmd.name),
                    group=EPILOG_COMMAND_HELP.group,
                )
            )

        self._format_epilog_parts(formatter, epilog_parts)

    def _include_common_options_epilog(self) -> bool:
        return True

    def _is_option_with_argument(self, option: click.Parameter) -> bool:
        if isinstance(option, ScopedOption):
            return option.has_argument()
        return False

    def _format_epilog_parts(self, formatter: HelpFormatter, parts: list[EpilogPart]):
        squashed_parts = []
        for idx, part in enumerate(parts):
            if (
                len(squashed_parts)
                and not part.title
                and part.group
                and part.group == squashed_parts[-1].group
            ):
                squashed_parts[-1].text += "\n\n" + part.text
                continue
            squashed_parts.append(part)

        for part in squashed_parts:
            self._format_epilog_part(formatter, part)

    def _format_epilog_part(self, formatter: HelpFormatter, part: EpilogPart):
        formatter.write_paragraph()
        if part.title:
            formatter.write_heading(part.title.capitalize(), newline=True, colon=False)

        with formatter.indentation():
            formatter.write_text(part.text)


class CliCommand(CliBaseCommand):
    option_scopes: list[OptionScope] = [
        OptionScope.COMMAND,
        OptionScope.GROUP,
    ]

    def __init__(self, **kwargs):
        kwargs.update(
            {
                "name": self._make_command_name(kwargs.get("name")),
                "params": self._build_options(kwargs.get("params", [])),
                "short_help": self._make_short_help(**kwargs),
            }
        )
        self.command_examples = Examples("Command examples", kwargs.pop("command_examples", []))
        self.output_examples = Examples("Output examples", kwargs.pop("output_examples", []))

        super().__init__(**kwargs)

    def _build_options(self, subclass_options: list[ScopedOption]) -> list[ScopedOption]:
        return [
            *subclass_options,
            *self._get_group_options(),
        ]

    def _get_group_options(self) -> list[ScopedOption]:
        return []

    def format_usage(self, ctx: Context, formatter: HelpFormatter) -> None:
        pieces = self.collect_usage_pieces(ctx)
        with formatter.section("Usage"):
            formatter.write_usage(ctx.command_path, " ".join(pieces), prefix="")

    def format_help_text(self, ctx: Context, formatter: HelpFormatter) -> None:
        super().format_help_text(ctx, formatter)
        self.format_examples(ctx, formatter, self.output_examples)
        self.format_own_command_type(ctx, formatter)

    def format_options(self, ctx: Context, formatter: HelpFormatter):
        opt_scope_to_opt_help_map: dict[str, list[tuple[str, str]] | None] = {
            k: [] for k in OptionScope
        }
        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is not None and hasattr(param, "scope"):
                opt_scope_to_opt_help_map[param.scope].append(rv)

        has_header = False
        for opt_scope in self.option_scopes:
            opt_helps = opt_scope_to_opt_help_map[opt_scope]
            if not opt_helps:
                continue
            if opt_scope.value:
                has_header = True
                with formatter.section(opt_scope.value):
                    formatter.write_dl(opt_helps)
            else:
                formatter.write_paragraph()
                with formatter.indentation():
                    formatter.write_dl(opt_helps)

        if any(self._is_option_with_argument(opt) for opt in ctx.command.params):
            formatter.write_paragraph()
            with formatter.indentation():
                formatter.write_text(inspect.cleandoc(EPILOG_ARGS_NOTE.text))

        self.format_common_options(ctx, formatter, not has_header)

    def format_epilog(self, ctx: Context, formatter: HelpFormatter) -> None:
        super().format_epilog(ctx, formatter)
        self.format_examples(ctx, formatter, self.command_examples)

    def format_examples(self, ctx: Context, formatter: HelpFormatter, examples: Examples) -> None:
        if not examples:
            return
        with formatter.section(examples.title.capitalize()):
            for example in examples.content:
                if "%s" in example:
                    example %= ctx.command_path
                formatter.write_text(example)


class CliGroup(click.Group, CliBaseCommand):
    TEXT_COMMAND_MATCHED_PART = FrozenStyle(fg=pt.cv.HI_BLUE, underlined=True)
    TEXT_COMMAND_SUGGEST_1ST_CHR = FrozenStyle(fg=pt.cv.HI_RED, bold=True, underlined=False)
    TEXT_COMMAND_SUGGEST_OTHERS = HelpStyles.TEXT_COMMAND_NAME

    def __init__(self, **kwargs):
        kwargs["name"] = self._make_command_name(kwargs.get("name"))
        kwargs["short_help"] = self._make_short_help(**kwargs)
        kwargs.setdefault("type", CMDTYPE_GROUP)

        super().__init__(**kwargs)

    def format_usage(self, ctx: Context, formatter: HelpFormatter) -> None:
        pieces = self.collect_usage_pieces(ctx)
        with formatter.section("Usage"):
            formatter.write_usage(ctx.command_path, " ".join(pieces), prefix="")

    def format_help_text(self, ctx: Context, formatter: HelpFormatter) -> None:
        super().format_help_text(ctx, formatter)
        self.format_own_command_type(ctx, formatter)

    def format_options(self, ctx: Context, formatter: HelpFormatter) -> None:
        # no options for groups
        self.format_commands(ctx, formatter)
        self.format_subcommand_types(formatter)

    def format_subcommand_types(self, formatter: HelpFormatter):
        cts = [
            *filter(
                lambda ct: ct.char and not ct.is_default,
                {*self.get_command_types()},
            )
        ]
        if not len(cts):
            return

        formatter.write_paragraph()
        with formatter.indentation():
            formatter.write_text(
                "   ".join(
                    formatter.format_command_type_desc(ct)
                    for ct in sorted(cts, key=lambda ct: ct.sorter)
                )
            )
        formatter.write_paragraph()

    def format_commands(self, ctx: Context, formatter: HelpFormatter) -> None:
        # modified version of parent implementation; could not inject otherwise
        commands = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            # What is this, the tool lied about a command.  Ignore it
            if cmd is None:
                continue
            if cmd.hidden:
                continue
            commands.append((subcommand, cmd))

        if len(commands):
            # +2 for command type
            limit = formatter.width - 6 - max(2 + len(cmd[0]) for cmd in commands)

            rows = []
            for subcommand, cmd in commands:
                help = cmd.get_short_help_str(limit)
                cmd_name = formatter.format_command_name_and_type(cmd)
                rows.append((cmd_name, help))

            if rows:
                with formatter.section("Commands"):
                    formatter.write_dl(rows, col_spacing=4)

    def add_commands(self, *commands: click.Command):
        for cmd in commands:
            self.add_command(cmd)

    def get_commands(self) -> dict[str, CliBaseCommand]:
        return cast(dict[str, CliBaseCommand], self.commands)

    def get_command(self, ctx, cmd_name) -> CliBaseCommand | None:
        rv = super().get_command(ctx, cmd_name)
        if rv is not None:
            return cast(CliBaseCommand, rv)

        matches = []
        lev_match = None
        for c in self.list_commands(ctx):
            if c.startswith(cmd_name):
                matches.append(c)
            if not lev_match and Levenshtein.distance(cmd_name, c) <= 1:
                lev_match = c

        if not matches:
            if not lev_match:
                get_logger().debug(f"No matches")
                return None
            get_logger().debug(f"Matched by levenstein distance: {lev_match}")
            return super().get_command(ctx, lev_match)
            # use closest levenstein match only if no exact matches
        elif len(matches) == 1:
            get_logger().debug(f"Matched by prefix: {matches[0]}")
            return super().get_command(ctx, matches[0])
        # matches > 1:

        stdout = get_stdout()
        def format_suggestions(m: t.Iterable[str]) -> str:
            suggs = [*map(lambda s: s.removeprefix(cmd_name), m)]
            same_chars_after = max(map(len, suggs))
            for i in range(same_chars_after):
                if any(len(s) <= i for s in suggs):
                    same_chars_after = i
                    break
                if len({*map(lambda s: s[i], suggs)}) > 1:   # unique characters at position <i>
                    same_chars_after = i+1
                    break
            get_logger().debug(f"Shortest unique seq. length = {same_chars_after:d}")
            return ', '.join(map(lambda s: format_suggestion(s, same_chars_after), suggs))

        def format_suggestion(s: str, same_chars_after: int) -> str:
            return (
                stdout.render(cmd_name, self.TEXT_COMMAND_MATCHED_PART)
                + stdout.render(s[:same_chars_after], self.TEXT_COMMAND_SUGGEST_1ST_CHR)
                + stdout.render(s[same_chars_after:], self.TEXT_COMMAND_SUGGEST_OTHERS)
            )

        msg = f"Several matches ({len(matches)}): {format_attrs(matches)}"
        ctx.fail(f"Several matches: {format_suggestions(sorted(matches))}")

    def resolve_command(self, ctx, args):
        # always return the full command name
        _, cmd, args = super().resolve_command(ctx, args)
        return cmd.name, cmd, args

    def get_command_types(self, recursive: bool = False) -> t.Iterable[CommandType]:
        for cmd in self.get_commands().values():
            if recursive and isinstance(cmd, CliGroup):
                yield from cmd.get_command_types(True)
            yield cmd.get_command_type()
