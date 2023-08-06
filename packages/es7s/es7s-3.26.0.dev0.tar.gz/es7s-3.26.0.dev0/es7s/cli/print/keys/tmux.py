# ------------------------------------------------------------------------------
#  es7s/core (G2)
#  (c) 2021-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
"""
Get a list of current tmux bindings, format it and display. Intended to run as
a tmux popup, but can be invoked directly as well.
"""
from __future__ import annotations

import re
import subprocess
import sys
import typing as t
from dataclasses import dataclass, field
from functools import total_ordering
from itertools import chain
from re import Pattern
from subprocess import SubprocessError, CompletedProcess, CalledProcessError
from typing import List, Dict, Sized, ClassVar, OrderedDict, Tuple, Callable

from pytermor import (
    NOOP_COLOR,
    NOOP_STYLE,
    DEFAULT_COLOR,
    Style,
    Text,
    center_sgr,
    cv,
    distribute_padded,
    get_terminal_width,
    ljust_sgr,
    rjust_sgr,
    IRenderer,
    Fragment,
)

from es7s.cli._base_opts_params import CMDTYPE_BUILTIN, CMDTRAIT_ADAPTIVE
from es7s.shared import get_stdout, FrozenStyle
from ..._base import CliCommand
from ..._decorators import _catch_and_log_and_exit, cli_command


class StyleRegistry:
    """
    Source of truth in `Style` context.
    """

    PAGE_HEADER_STYLE = Style(fg=cv.GRAY_35, bg=cv.GRAY_7)
    TABLE_HEADER_STYLE = Style(bold=True)
    KEY_TABLE_NAME_STYLE = Style(TABLE_HEADER_STYLE, fg=cv.YELLOW)
    KEY_STYLE = Style(bg=cv.GRAY_3)
    MOUSE_KEY_STYLE = Style(bg=cv.GRAY_3, italic=True)
    INVOKER_KEY_STYLE = Style(KEY_STYLE, fg=cv.RED)

    DOMAIN_TO_DOMAIN_STYLE_MAP: Dict[Pattern, Style] = {
        re.compile("^$"): NOOP_STYLE,
        re.compile("^mode$"): Style(fg=cv.YELLOW),
        re.compile("^es7s$"): Style(fg=cv.BLUE),
        re.compile("^x11$"): Style(fg=cv.CYAN),
        re.compile("^w/a$"): Style(fg=cv.CYAN),
        re.compile("^.+$"): Style(fg=cv.MAGENTA),
    }
    DOMAIN_TO_DESC_STYLE_MAP: Dict[Pattern, Style] = {
        re.compile("^(x11|w/a)$"): Style(dim=True),
    }

    CONFIRMATION_REQ_STYLE = Style(fg=cv.HI_YELLOW)
    NO_CONFIRMATION_STYLE = Style(fg=cv.HI_RED)
    TUNNELABLE_STYLE = Style(fg=cv.HI_CYAN)

    MODIFIER_ALT_STYLE = Style(fg=cv.HI_GREEN, bg=cv.DARK_GREEN)
    MODIFIER_CTRL_STYLE = Style(fg=cv.HI_RED, bg=cv.DARK_RED_2)
    MODIFIER_SHIFT_STYLE = Style(fg=cv.HI_CYAN, bg=cv.DEEP_SKY_BLUE_7)
    MODIFIER_WIN_STYLE = Style(fg=cv.HI_BLUE, bg=cv.PURPLE_6)
    MODIFIER_SEPARATOR_STYLE = Style(KEY_STYLE, fg=cv.GRAY_35)

    @classmethod
    def get_column_style(cls, column_attr: str, domain: str) -> Style:
        if column_attr == "sequence":
            return NOOP_STYLE
        if column_attr == "combo":
            return cls.KEY_STYLE
        if column_attr == "desc":
            return cls._match_map(domain, cls.DOMAIN_TO_DESC_STYLE_MAP)
        if column_attr == "desc_dot":
            return cls.get_domain_style(domain)
        if column_attr == "domain":
            return Style(cls.get_domain_style(domain), dim=True)
        raise KeyError(f"Invalid column attribute {column_attr}")

    @classmethod
    def get_domain_style(cls, domain: str) -> Style:
        return cls._match_map(domain, cls.DOMAIN_TO_DOMAIN_STYLE_MAP)

    @classmethod
    def _match_map(cls, subject: str | None, style_map: Dict[Pattern, Style]) -> Style:
        for regex, style in style_map.items():
            if regex.fullmatch(subject or ""):
                return style
        return NOOP_STYLE


@total_ordering
@dataclass(repr=False)
class Sequence(Fragment):
    """
    Set of keystrokes.
    That's what tmux returns with `list-keys` command:
        <Keystrokes>      <Action>
    Example: "C-a C-z" (Ctrl+A, Ctrl+Z) -- default tmux sequence to suspend current client.
    """

    COMBO_PAD = " " * 1

    combos: List[KeyCombo]

    def render(self, _=None) -> str:
        return get_stdout().render(self.COMBO_PAD.join([c.render() for c in self.combos]))

    def __len__(self) -> int:
        return len(self.COMBO_PAD.join("c" * len(c) for c in self.combos))

    def __repr__(self) -> str:
        combos = [f"{c!r}" for c in self.combos]
        return self.__class__.__name__ + "[" + ",".join(combos) + "]"

    def __lt__(self, other: Sequence) -> bool:
        return self._compare(other) == -1

    def __eq__(self, other: Sequence) -> bool:
        return self._compare(other) == 0

    def _compare(self, other: Sequence) -> int:
        max_i = max(len(self.combos), len(other.combos))
        for i in range(0, max_i):
            if i >= len(self.combos):
                return 1
            if i >= len(other.combos):
                return -1
            if self.combos[i] > other.combos[i]:
                return 1
            if self.combos[i] < other.combos[i]:
                return -1
        return 0


@dataclass
class KeyCombo(Fragment, Sized):
    """
    Combination of *one* key and zero/one/more modifiers.
    Example: "C-b" (Ctrl+B), default prefix key binding.
    """

    MODIFIER_SEPARATOR = "-"
    KEY_PAD = " " * 1

    key: Key
    mods: List[Modifier]

    def __post_init__(self):
        self._string = self.key.label + "".join([mod.label for mod in self.mods])

    def render(self, renderer: IRenderer | t.Type[IRenderer] = None) -> str:
        rendered = ""
        key_style = StyleRegistry.KEY_STYLE
        mod_sep_style = StyleRegistry.MODIFIER_SEPARATOR_STYLE

        override_key_style = None
        if self.is_invoker:
            override_key_style = StyleRegistry.INVOKER_KEY_STYLE

        for mod in self.mods:
            rendered += mod.render()
            rendered += get_stdout().render(self.MODIFIER_SEPARATOR, mod_sep_style)

        if len(rendered) == 0:
            rendered += get_stdout().render(self.KEY_PAD, key_style)

        rendered += self.key.render(override_key_style)
        rendered += get_stdout().render(self.KEY_PAD, key_style)
        return rendered

    def __add__(self, other):
        return self.render() + other

    @property
    def is_invoker(self) -> bool:
        return (
            len(self.mods) == 1
            and ModifierRegistry.MODIFIER_CTRL in self.mods
            and self.key.label in KeyTableRegistry.INVOKERS
        )

    def __len__(self) -> int:
        result = 0
        for mod in self.mods:
            result += len(mod) + len(self.MODIFIER_SEPARATOR)
        if result == 0:
            result += len(self.KEY_PAD)
        return result + len(self.key) + len(self.KEY_PAD)

    def __repr__(self) -> str:
        mods = [f"{m.code}-" for m in self.mods]
        return self.__class__.__name__ + "[" + "".join(mods) + self.key.label + "]"

    def __lt__(self, other: KeyCombo) -> bool:
        return self._compare(other) < 0

    def __eq__(self, other: KeyCombo) -> bool:
        return self._compare(other) == 0

    def _compare(self, other: KeyCombo) -> int:
        result = 0
        if self.is_invoker:
            result += 10
        if other.is_invoker:
            result -= 10

        max_i = max(len(self.mods), len(other.mods))
        for i in range(0, max_i):
            if i >= len(self.mods):
                return result + 1
            if i >= len(other.mods):
                return result - 1
            if self.mods[i] > other.mods[i]:
                return result + 1
            if self.mods[i] < other.mods[i]:
                return result - 1

        if self.key > other.key:
            return result - 1
        if self.key < other.key:
            return result + 1
        return result


class KeyComboFactory:
    """
    Class that breaks down string key description into key definition and modifiers
    as a separate list, e.g: "M-S-Right" will become {Sequence} consisting
    of: {Key} "Right", {Modifier} "Alt", {Modifier} "Shift".
    """

    MODIFIER_REGEXP = re.compile(r"^([MCSW])-")

    @classmethod
    def from_tmux_output(cls, raw_combo: str) -> KeyCombo:
        mods = []
        while mod_match := cls.MODIFIER_REGEXP.match(raw_combo):
            mods += [ModifierRegistry.find_by_code(mod_match.group(1))]
            raw_combo = raw_combo[mod_match.end(0) :]
        return KeyCombo(Key(raw_combo), mods)


def char_range(c1, c2):
    """Generates the characters from `c1` to `c2`, inclusive."""
    for c in range(ord(c1), ord(c2) + 1):
        yield chr(c)


def flatten(list_of_lists):
    """Flatten one level of nesting."""
    return chain.from_iterable(list_of_lists)


@total_ordering
@dataclass
class Key(Fragment, Sized):
    """
    Definition of a key.
    Examples: 'q', '1', 'Space', 'Enter'.
    """

    MOUSE_KEYS = ["lbutton"]

    LABEL_LEFT = "←"
    LABEL_RIGHT = "→"
    LABEL_UP = "↑"
    LABEL_DOWN = "↓"
    LABEL_UP_DOWN = "⇅"

    LABEL_OVERRIDE = {
        "Left": LABEL_LEFT,
        "Right": LABEL_RIGHT,
        "Up": LABEL_UP,
        "Down": LABEL_DOWN,
        "Arrows": LABEL_LEFT + LABEL_UP_DOWN + LABEL_RIGHT,
    }

    LABEL_TO_SORTER_MAP: ClassVar[OrderedDict[str, int]] = {
        char: idx
        for idx, char in enumerate(
            [
                *flatten([c, c.upper()] for c in char_range("a", "z")),
                *"~`!@#$%^&*()-_=+[]{}\\|;:'\",.<>/?",
                *char_range("0", "9"),
                *LABEL_OVERRIDE.values(),
            ]
        )
    }

    label: str
    _sorter: int = field(default=len(LABEL_TO_SORTER_MAP), init=False)

    def __post_init__(self):
        for pattern, replace in self.LABEL_OVERRIDE.items():
            self.label = re.sub(pattern, replace, self.label)

        if len(self.label) == 1:
            self._sorter = self.LABEL_TO_SORTER_MAP.get(self.label[0], 0)
        # else sort by a label (as string)

    @property
    def _style(self) -> Style:
        if self.is_mouse_key:
            return StyleRegistry.MOUSE_KEY_STYLE
        return StyleRegistry.KEY_STYLE

    @property
    def is_mouse_key(self) -> bool:
        return self.label.lower() in self.MOUSE_KEYS

    def render(self, override_style: Style = None) -> str:
        return get_stdout().render(self.label, (override_style or self._style))

    def __len__(self) -> int:
        return len(self.label)

    def __lt__(self, other: Key) -> bool:
        return self._compare(other) < 0

    def __eq__(self, other: Key) -> bool:
        return self._compare(other) == 0

    def _compare(self, other: Key) -> int:
        result = self._sorter - other._sorter

        if result == 0:
            if self.label > other.label:
                return result + 1
            if self.label < other.label:
                return result - 1
        return result


@total_ordering
@dataclass
class Modifier(Fragment, Sized):
    """
    Definition of supplementary key that doesn't have any actions bound, but
    instead alternates the action bound to other key.

    Default modifiers:
        C       Control
        M       Meta/Alt
        S       Shift
        W       Win/Super (x11 extension)
    """

    code: str
    out: str
    label: str
    style: Style = NOOP_STYLE

    def render(self, renderer: IRenderer | t.Type[IRenderer] = None) -> str:
        return get_stdout().render(self.out, self.style)

    def format_legend(self) -> Text:
        label_style = FrozenStyle(self.style, fg=DEFAULT_COLOR)
        first_ch_style = FrozenStyle(self.style, bold=True)
        return Fragment(KeyCombo.KEY_PAD + self.label[0], first_ch_style) + Fragment(
            f"{self.label[1:]}{KeyCombo.KEY_PAD}", label_style
        )

    def __len__(self) -> int:
        return len(self.out)

    def __lt__(self, other: Modifier) -> bool:
        return self._sorter < other._sorter

    def __eq__(self, other: Modifier) -> bool:
        return self._sorter == other._sorter

    @property
    def _sorter(self):
        return -list(ModifierRegistry.MODIFIER_CODES_MAP.keys()).index(self.code)


class ModifierRegistry:
    """
    Modifier defaults.
    """

    MODIFIER_CTRL = Modifier("C", out="C", label="Control", style=StyleRegistry.MODIFIER_CTRL_STYLE)
    MODIFIER_ALT = Modifier("M", out="M", label="Meta/Alt", style=StyleRegistry.MODIFIER_ALT_STYLE)
    MODIFIER_SHIFT = Modifier("S", out="S", label="Shift", style=StyleRegistry.MODIFIER_SHIFT_STYLE)
    MODIFIER_WIN = Modifier("W", out="W", label="Win/Super", style=StyleRegistry.MODIFIER_WIN_STYLE)

    MODIFIER_CODES_MAP: Dict[str, Modifier] = {
        MODIFIER_CTRL.code: MODIFIER_CTRL,
        MODIFIER_ALT.code: MODIFIER_ALT,
        MODIFIER_SHIFT.code: MODIFIER_SHIFT,
        MODIFIER_WIN.code: MODIFIER_WIN,
    }

    @classmethod
    def find_by_code(cls, code: str) -> Modifier:
        if code not in cls.MODIFIER_CODES_MAP.keys():
            raise KeyError(f'No modifier with combo "{code}" is registered')
        return cls.MODIFIER_CODES_MAP.get(code)


class KeyTableRegistry:
    """
    es7s/tmux key table and prefixes.
    """

    INVOKER_PRIMARY = "a"
    INVOKER_COMPAT = "b"
    INVOKERS = [
        INVOKER_PRIMARY,
        INVOKER_COMPAT,
    ]

    KEY_TABLES_PREFIX_MAP: Dict[str, KeyCombo | None] = {
        "root": None,
        "prefix": KeyCombo(
            Key(INVOKER_PRIMARY), [ModifierRegistry.MODIFIER_CTRL]
        ),  # @FIXME request tmux for actual values
        "compat": KeyCombo(Key(INVOKER_COMPAT), [ModifierRegistry.MODIFIER_CTRL]),
        "copy-mode": None,
        "x11": None,
    }
    KEY_TABLES_TMUX = ["root", "prefix", "compat", "copy-mode"]


@total_ordering
@dataclass
class Bind:
    """
    Instance that defines binding some action with some key sequence.
    Example: "S-Up" sequence <-> "create new window" action.
    """

    DOMAIN_TO_SORTER_MAP = {
        "x11": -10,
        "w/a": -20,
    }

    parent_table: BindKeyTable = None
    sequence: Sequence = None
    desc: Fragment = None
    domain: str = None

    @staticmethod
    def get_renderable_attrs() -> List[str]:
        return ["sequence", "desc_dot", "desc", "domain"]

    def pad_attr(self, attr: str) -> bool:
        return attr in ["sequence", "desc"]

    def align_fn(self, attr: str) -> Callable[[str, int], str]:
        return rjust_sgr if attr in ["domain"] else ljust_sgr

    @property
    def desc_dot(self):
        return "·" if self.domain else " "

    def render_column(self, attr: str, col_style: Style) -> str:
        raw_val = getattr(self, attr) or ""
        max_len = self.parent_table.get_attr_max_len(attr)

        if isinstance(raw_val, Fragment) or isinstance(raw_val, Text):
            rendered = raw_val.render()  # @FIXME reduce too
        else:
            rendered = get_stdout().render(raw_val[:max_len], col_style)

        return self.align_fn(attr)(rendered, max_len)

    def __repr__(self) -> str:
        return (
            self.__class__.__name__
            + f"[{(self.parent_table.name if self.parent_table else None)}, {self.sequence!r}, {self.desc.render()}, {self.domain}]"
        )

    def __lt__(self, other: Bind) -> bool:
        return self._compare(other) > 0

    def __eq__(self, other: Bind) -> bool:
        return self._compare(other) == 0

    @property
    def _sorter(self) -> int:
        return self.DOMAIN_TO_SORTER_MAP.get(self.domain, 0)

    def _compare(self, other: Bind) -> int:
        result = self._sorter - other._sorter

        if self.sequence > other.sequence:
            return result + 1
        if self.sequence < other.sequence:
            return result - 1
        return result


class BindKeyTable:
    def __init__(self, name: str):
        self.name = name
        self.binds: List[Bind] = []
        self._attrs_col_width_map: Dict[str, int] = dict(
            {k: 0 for k in Bind.get_renderable_attrs()}
        )

    def append(self, bind: Bind):
        self.binds.append(bind)

    def sort(self):
        self.binds.sort()

    def update_attrs_col_width(self):
        for bind in self.binds:
            for attr in Bind.get_renderable_attrs():
                cur_len = len(getattr(bind, attr) or "")
                max_len = self._attrs_col_width_map.get(attr)
                if max_len < cur_len:
                    self.set_attr_max_len(attr, cur_len)

    def get_attr_max_len(self, attr: str) -> int:
        return self._attrs_col_width_map.get(attr)

    def set_attr_max_len(self, attr: str, max_len: int):
        self._attrs_col_width_map[attr] = max(0, max_len)

    def __repr__(self) -> str:
        return self.__class__.__name__ + f"[{len(self.binds)}]"


class BindCollection:
    """
    Set of bindings grouped by key table.
    """

    def __init__(self, raw_binds: List[str]):
        raw_binds = self._add_manual_binds(raw_binds)

        self.key_tables: Dict[str, BindKeyTable] = {
            k: BindKeyTable(k) for k in KeyTableRegistry.KEY_TABLES_PREFIX_MAP.keys()
        }
        self.parse(raw_binds)

    def parse(self, raw_binds: List[str]):
        for raw_bind in raw_binds:
            bind, key_table_name = BindFactory.from_tmux_output(raw_bind)
            if key_table_name not in self.key_tables.keys():
                raise KeyError(f'Unknown key table "{key_table_name}" for {bind}')

            key_table = self.key_tables[key_table_name]
            key_table.append(bind)
            bind.parent_table = key_table

        for key_table in self.key_tables.values():
            key_table.sort()
            key_table.update_attrs_col_width()

    def _add_manual_binds(self, raw_binds: List[str]) -> List[str]:
        raw_binds.insert(0, "root  C-a  [mode] Invoke prefix key table")
        raw_binds.append("x11  M-Escape      Show/hide terminal")
        raw_binds.append("x11  M-`      Show/hide terminal")
        raw_binds.append("x11  W-S      Switch workspaces")
        raw_binds.append("x11  C-M-/      delayed-screenshot")
        raw_binds.append("x11  M-LButton      faststack")
        raw_binds.append("x11  M-S-LButton      faststack --close")
        return raw_binds

    def __repr__(self) -> str:
        return self.__class__.__name__ + f"[{len(self.key_tables)}]"


class BindFactory:
    """
    tmux `list-keys` output parser.
    """

    @staticmethod
    def from_tmux_output(raw_bind: str) -> Tuple[Bind, str]:
        splitted = [s.strip() for s in re.split(r"\x1f|\s+", raw_bind)]
        bind = Bind()

        key_table = splitted[0]

        prefix = KeyTableRegistry.KEY_TABLES_PREFIX_MAP.get(key_table)
        main = KeyComboFactory.from_tmux_output(splitted[1])
        bind.sequence = Sequence([v for v in [prefix, main] if isinstance(v, KeyCombo)])

        right_parts: List[str] = splitted[2:]
        if domain_match := re.fullmatch(r"^\[(.+)]$", right_parts[0]):
            bind.domain = domain_match.group(1)
            right_parts.pop(0)

        desc_st = StyleRegistry.get_column_style("desc", bind.domain)
        desc = Text(Fragment("", fmt=desc_st, close_this=False))
        for rp in right_parts:
            desc += " " + BindFactory._apply_inline_attribute_format(rp)
        bind.desc = desc

        return bind, key_table

    @staticmethod
    def _apply_inline_attribute_format(word: str) -> Text | Fragment:
        if word.endswith("?"):
            return Fragment(word[:-1]) + Fragment(word[-1], StyleRegistry.CONFIRMATION_REQ_STYLE)
        elif word.endswith("!"):
            return Fragment(word[:-1]) + Fragment(word[-1], StyleRegistry.NO_CONFIRMATION_STYLE)
        elif word.endswith("↡"):
            return Fragment(word[:-1]) + Fragment(word[-1], StyleRegistry.TUNNELABLE_STYLE)
        return Fragment(word)


class TmuxExecutor:
    """
    tmux `list-keys` argument compiler and command runner.
    """

    @staticmethod
    def get_raw_binds() -> List[str]:
        list_keys_cmd_args = ["tmux"]
        for key_table in KeyTableRegistry.KEY_TABLES_TMUX:
            list_keys_cmd_args += ["list-keys", "-aNP", f"{key_table}\x1f", "-T", f"{key_table};"]
        try:
            p: CompletedProcess = subprocess.run(
                list_keys_cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf8",
                check=True,
            )
        except CalledProcessError as _e:
            raise SubprocessError("Failed to get raw binds from tmux") from _e
        return p.stdout.splitlines()


class PopupFormatter:
    """
    Output formatter for tmux popup.
    """

    OUT = sys.stdout

    PAGE_PAD: str = " " * 2
    COL_PAD = " " * 1
    SECT_PAD = " " * 4
    DOMAIN_DISPLAY_TERMW_THRESHOLD = 45

    @classmethod
    def print_legend(cls):
        # @rewrite after pytermor 2.4+ is available
        defbg = StyleRegistry.PAGE_HEADER_STYLE.bg
        colpad = Text(cls.COL_PAD, StyleRegistry.PAGE_HEADER_STYLE)
        sectpad = Text(cls.SECT_PAD, StyleRegistry.PAGE_HEADER_STYLE)

        def print_items():
            yield Text(cls.PAGE_PAD + "LEGEND", StyleRegistry.PAGE_HEADER_STYLE)
            yield sectpad
            yield from [
                Text(" Key ", Style(StyleRegistry.KEY_STYLE, bg=cv.GRAY_0)),
                colpad,
                Text(" MBtn ", Style(StyleRegistry.MOUSE_KEY_STYLE, bg=cv.GRAY_0)),
            ]
            yield sectpad
            for idx, mod in enumerate(ModifierRegistry.MODIFIER_CODES_MAP.values()):
                if idx > 0:
                    yield colpad
                yield mod.format_legend()
            yield sectpad
            yield from [
                Text("?", Style(StyleRegistry.CONFIRMATION_REQ_STYLE, bg=defbg)),
                Text(" Confirm before", Style(bg=defbg)),
                colpad,
                colpad,
                Text("!", Style(StyleRegistry.NO_CONFIRMATION_STYLE, bg=defbg)),
                Text(" No confirm", Style(bg=defbg)),
                colpad,
                colpad,
                Text("↡", Style(StyleRegistry.TUNNELABLE_STYLE, bg=defbg)),
                Text(" Tunnels down", Style(bg=defbg)),
            ]

        line = Text()
        for item in print_items():
            line += item

        blank = Text(
            cls.PAGE_PAD + " " * max(get_terminal_width(), len(line.raw())),
            StyleRegistry.PAGE_HEADER_STYLE,
        )
        get_stdout().echo_rendered(blank)
        get_stdout().echo_rendered(
            line
            + Fragment(
                " " * (get_terminal_width() - len(line.raw())) + cls.PAGE_PAD,
                StyleRegistry.PAGE_HEADER_STYLE,
            ),
        )
        get_stdout().echo_rendered(blank)
        get_stdout().echo()

    @classmethod
    def print_binds(cls, binds: BindCollection):
        attrs_render_list = Bind.get_renderable_attrs()
        if (termw := get_terminal_width()) <= cls.DOMAIN_DISPLAY_TERMW_THRESHOLD:
            attrs_render_list.remove("domain")
            for key_table in binds.key_tables.values():
                key_table.set_attr_max_len("domain", 0)

        for key_table in binds.key_tables.values():
            cls._compute_max_desc_len(key_table, attrs_render_list)

            label = "KEY TABLE"
            if key_table.name not in KeyTableRegistry.KEY_TABLES_TMUX:
                label = "SUPPLEMENTARY GLOBALS"
            get_stdout().echo(
                cls.PAGE_PAD
                + get_stdout().render(label, StyleRegistry.TABLE_HEADER_STYLE)
                + "  "
                + get_stdout().render(key_table.name, StyleRegistry.KEY_TABLE_NAME_STYLE)
                + "  "
                + get_stdout().render(
                    " " * (termw - len(key_table.name) - len(label) - 5),
                    Style(fg=cv.GRAY_23, crosslined=True),
                )
                + " ",
            )
            get_stdout().echo()

            for bind in key_table.binds:
                columns_rendered = cls.PAGE_PAD + cls.COL_PAD  # for leftmost pad

                for attr in attrs_render_list:
                    col_style = StyleRegistry.get_column_style(attr, bind.domain)
                    column_rendered = bind.render_column(attr, col_style)
                    if bind.pad_attr(attr):
                        column_rendered += cls.COL_PAD
                    columns_rendered += column_rendered
                get_stdout().echo(columns_rendered)

            get_stdout().echo()

    @classmethod
    def print_cheatsheet(cls):
        key_any = Key("(Arrows)")
        key_lr = Key("(Left Right)")
        key_ud = Key("(Up Down)")
        key_np = Key("(n p)")
        mod_a = ModifierRegistry.MODIFIER_ALT
        mod_c = ModifierRegistry.MODIFIER_CTRL
        mod_s = ModifierRegistry.MODIFIER_SHIFT
        pref = KeyTableRegistry.KEY_TABLES_PREFIX_MAP["prefix"]
        pref_compat = KeyTableRegistry.KEY_TABLES_PREFIX_MAP["compat"]
        kc_any = KeyCombo(key_any, [])
        kc_any_modc = KeyCombo(key_any, [mod_c])
        kc_np = KeyCombo(key_np, [])
        kc_lr_mods = KeyCombo(key_lr, [mod_s])
        kc_u_mods = KeyCombo(Key("( Up )"), [mod_s])
        kc_u_modc = KeyCombo(Key("( Up )"), [mod_c])
        kc_d_mods = KeyCombo(Key("( Down )"), [mod_s])
        kc_lr_modcs = KeyCombo(key_lr, [mod_c, mod_s])
        kc_lr_modc = KeyCombo(key_lr, [mod_c])
        kc_lr_moda = KeyCombo(key_lr, [mod_a])
        kc_ud_moda = KeyCombo(key_ud, [mod_a])
        disabled_st = Style(StyleRegistry.MODIFIER_SEPARATOR_STYLE, bg=NOOP_COLOR)
        lbl_same = "[same]"
        lbl_none = get_stdout().render("none", disabled_st)
        note = get_stdout().render("*", disabled_st)

        cls.print_padded("")
        cls.print_padded(Fragment("ARROW KEYS BINDINGS", StyleRegistry.TABLE_HEADER_STYLE).render())
        cls.print_padded("")
        # fmt: off
        cls.print_padded(
'┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓' + '\n' +
'┃          BINDING           ┃    DEFAULT    ┃ COMPATIBILITY'+note+'┃' + '\n' +
'┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━┛' + '\n' +
'║ Move cursor                │ {} │ {} ║'.format(
    distribute_padded(13, '', kc_any),
    center_sgr(lbl_same, 13),
) + '\n' +
'║ Move cursor by block/word  │ {} │ {} ║'.format(distribute_padded(13, '', KeyCombo(key_any, [mod_c])), center_sgr(lbl_same, 13)) + '\n' +
'╟────────────────────────────┼───────────────┼───────────────╢' + '\n' +
'║ Select PANE                │ {} │ {} ║'.format(distribute_padded(13, '', KeyCombo(key_any, [mod_a])), distribute_padded(13, pref_compat, kc_any)) + '\n' +
'║ Resize PANE                │ {} │ {} ║'.format(distribute_padded(13, '', KeyCombo(key_any, [mod_a, mod_s])), center_sgr(lbl_none, 13)) + '\n' +
'║ Select WINDOW              │ {} │ {} ║'.format(distribute_padded(13, '', kc_lr_mods), distribute_padded(13, pref_compat, kc_lr_modc)) + '\n' +
'║ Create WINDOW              │ {} │ {} ║'.format(distribute_padded(13, '', kc_u_mods), distribute_padded(13, pref_compat, kc_u_modc)) + '\n' +
'║ Kill{} WINDOW               │ {} │ {} ║'.format(get_stdout().render('?', StyleRegistry.CONFIRMATION_REQ_STYLE), distribute_padded(13, '', kc_d_mods), center_sgr(lbl_none, 13)) + '\n' +
'║ Select WINDOW with alarm   │ {} │ {} ║'.format(distribute_padded(13, '', kc_lr_modcs), center_sgr(lbl_none, 13)) + '\n' +
'╟────────────────────────────┼───────────────┼───────────────╢' + '\n' +
'║ Split PANE                 │ {} │ {} ║'.format(distribute_padded(13, pref, kc_any), center_sgr(lbl_same, 13)) + '\n' +
'║ Split WINDOW               │ {} │ {} ║'.format(distribute_padded(13, pref, kc_any_modc), center_sgr(lbl_same, 13)) + '\n' +
'║ Rotate PANES               │ {} │ {} ║'.format(distribute_padded(13, pref, kc_lr_moda), center_sgr(lbl_none, 13)) + '\n' +
'║ Swap PANES by index        │ {} │ {} ║'.format(distribute_padded(13, pref, kc_ud_moda), center_sgr(lbl_none, 13)) + '\n' +
'║ Select SESSION             │ {} │ {} ║'.format(distribute_padded(13, pref, kc_lr_mods), center_sgr(lbl_none, 13)) + '\n' +
'║ Create SESSION             │ {} │ {} ║'.format(distribute_padded(13, pref, kc_u_mods), center_sgr(lbl_none, 13)) + '\n' +
'╚════════════════════════════╧═══════════════╧═══════════════╝', pad_mult=2)
        cls.print_padded(get_stdout().render('  The reason for compatibility mode bindings is existence of\n'+
                                 '  ssh clients without support of Alt+Arrows and Shift+Arrows\n'+
                                 '  combinations, e.g. JuiceSSH for Android.\n', disabled_st), pad_mult=2)
        # fmt: on

    @classmethod
    def print_padded(cls, s, pad_mult=1):
        get_stdout().echo(
            "\n".join(((pad_mult * cls.PAGE_PAD) + l) for l in s.splitlines())
        )  # noqa

    @classmethod
    def _compute_max_desc_len(cls, key_table: BindKeyTable, attrs_render_list: List[str]):
        total_len = sum(key_table.get_attr_max_len(attr) for attr in attrs_render_list) + len(
            cls.COL_PAD
        ) * len(
            attrs_render_list
        )  # pads between columns + leftmost
        term_width = get_terminal_width()

        delta = term_width - total_len
        key_table.set_attr_max_len("desc", key_table.get_attr_max_len("desc") + delta)


@cli_command(
    name=__file__,
    cls=CliCommand,
    type=CMDTYPE_BUILTIN,
    traits=[CMDTRAIT_ADAPTIVE],
    short_help="current tmux bindings",
)
@_catch_and_log_and_exit
class TmuxKeysCommand:
    """
    a
    """

    def __init__(self, **kwargs):
        self.run()

    def run(self):
        # pager/tmux are not ttys, so library autoconfig prevents SGRs by default. override it:
        # RendererManager.set_default_format_always()

        raw_binds = TmuxExecutor.get_raw_binds()
        binds = BindCollection(raw_binds)

        PopupFormatter.print_legend()
        PopupFormatter.print_binds(binds)
        PopupFormatter.print_cheatsheet()
