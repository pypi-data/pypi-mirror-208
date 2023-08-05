# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2021-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

import click
import pytermor as pt

from es7s.shared import get_stdout, FrozenStyle
from .._base import CliCommand
from .._base_opts_params import CMDTYPE_DYNAMIC
from .._decorators import cli_pass_context, _catch_and_log_and_exit, cli_command


@cli_command(
    name=__file__,
    cls=CliCommand,
    type=CMDTYPE_DYNAMIC,
    short_help="python regular expressions",
)
@cli_pass_context
@_catch_and_log_and_exit
class RegexPrinter:
    """
    Display python regular expressions cheatsheet.

    For best results view it on a terminal at least 180 characters wide, although
    anything down to 88 chars is good enough, too. Consider piping the output to
    a pager if width of your terminal is less than that. Use '-c' option to force
    formatting in the output, because the app disables it by default, if detects
    a pipe or redirection.
    """

    CUSTOM_STYLES = {
        "title": FrozenStyle(
            fg="true-white",
            bold=True,
            underlined=True,
            overlined=True,
        ),
        "header": FrozenStyle(fg="yellow", bold=True),
        "t": FrozenStyle(fg="green"),
        "n": FrozenStyle(fg="red"),
        "fn": FrozenStyle(fg="blue"),
        "url": FrozenStyle(underlined=True),
        "hl": FrozenStyle(italic=True),
        "comment": FrozenStyle(fg=pt.cv.GRAY_35),
    }
    PADDING = 4

    DATA_SEGS = [
        r"""
 :[|title]PYTHON REGULAR EXPRESSIONS:[-title]                                             :[comment]relevant for:[-comment]
 _[      ]                          _[      ]                                               :[comment]3.8 / 3.10:[-comment]
 :[header]SPECIAL CHARACTERS:[-header]
  :[t].:[-t]         Matches any character except a newline.
  :[t]^:[-t]         Matches the start of the string.
  :[t]$:[-t]         Matches the end of the string or just before the newline at
  _[ ] _[  ]         the end of the string.
  :[t]*:[-t]         Matches 0 or more (:[hl]greedy:[-hl]) repetitions of the preceding RE.
  _[ ] _[  ]         :[hl]Greedy:[-hl] means that it will match as many repetitions as possible.
  :[t]+:[-t]         Matches 1 or more (:[hl]greedy:[-hl]) repetitions of the preceding RE.
  :[t]?:[-t]         Matches 0 or 1 (:[hl]greedy:[-hl]) of the preceding RE.
  :[|t]*?,+?,??:[-t]  :[hl]Non-greedy:[-hl] versions of the previous three special characters.
  :[t]{m,n}:[-t]     Matches from :[t]m:[-t] to :[t]n:[-t] repetitions of the preceding RE.
  :[t]{m,n}?:[-t]    :[hl]Non-greedy:[-hl] version of the above.
  :[t]\:[-t]         Either escapes special characters or signals a special sequence.
  :[t][]:[-t]        Set of characters. :[t]^:[-t] as the 1st char indicates a complementing set.
  :[t]|:[-t]         :[t]A|B:[-t] creates an RE that will match either :[t]A:[-t] or :[t]B:[-t].
  :[t](...):[-t]     Matches :[t]...:[-t]; the contents can be retrieved or matched later.
  :[t](?:...):[-t]   :[hl]Non-grouping:[-hl] version of regular parentheses.
  :[t](?#...):[-t]   A comment; ignored.
  :[t](?aiLmsux):[-t]       The letters set the corresponding :[fn]flags:[-fn] defined below.
  :[t](?P<name>...):[-t]    The substring matched by the group is accessible by :[t]name:[-t].
  :[t](?P=name):[-t]        Matches the text matched earlier by the group named :[t]name:[-t].
  :[t](?(id/name)y|n):[-t]  Matches :[t]y:[-t] pattern if the group with :[t]id/name:[-t] matched,
  _[ ]               _[  ]  the (optional) :[t]n:[-t] pattern otherwise.
  :[t](?=...):[-t]   :[hl]Positive lookahead:[-hl]: matches if :[t]...:[-t] matches next, doesn't consume it.
  :[t](?!...):[-t]   :[hl]Negative lookahead:[-hl]: matches if :[t]...:[-t] doesn't match next.
  :[t](?<=...):[-t]  :[hl]Positive lookbehind:[-hl]: matches if preceded by :[t]...:[-t] (must be fixed length).
  :[t](?<!...):[-t]  :[hl]Negative lookbehind:[-hl]: matches if not preceded by :[t]...:[-t] (must be fixed length).""",
        r"""
 :[header]SPECIAL SEQUENCES:[-header]
  :[t]\num:[-t]     Matches the contents of the group of the same :[t]num:[-t]ber.
  :[t]\A:[-t]       Matches only at the start of the string.
  :[t]\Z:[-t]       Matches only at the end of the string.
  :[t]\b:[-t]       Matches the empty string, but only at the start or end of a word.
  :[t]\B:[-t]       Matches the empty string, but not at the start or end of a word.
  :[t]\d:[-t]       Matches any decimal digit; equivalent to the set :[t][0-9]:[-t] in
  _[ ]  _[  ]       bytes patterns or string patterns with the :[fn]ASCII:[-fn] flag.
  _[ ]  _[  ]       In string patterns without the :[fn]ASCII:[-fn] flag, it will match the whole
  _[ ]  _[  ]       range of Unicode digits.
  :[t]\D:[-t]       Matches any non-digit character; equivalent to :[t][^\d]:[-t].
  :[n]\p{<L>}:[-n]  Unicode properties shortcuts (incl. :[n]\P{<L>}:[-n]). Python doesn't
  _[ ]       _[  ]  support them out-of-the-box; see :[url]https://pypi.org/project/regex/:[-url].
  :[t]\s:[-t]       Matches any whitespace character; equivalent to :[t][ \t\n\r\f\v]:[-t] in
  _[ ]  _[  ]       bytes patterns or string patterns with the :[fn]ASCII:[-fn] flag.
  _[ ]  _[  ]       In string patterns without the :[fn]ASCII:[-fn] flag, it will match the whole
  _[ ]  _[  ]       range of Unicode whitespace characters.
  :[t]\S:[-t]       Matches any non-whitespace character; equivalent to :[t][^\s]:[-t].
  :[t]\w:[-t]       Matches any alphanumeric character; equivalent to :[t][a-zA-Z0-9_]:[-t]
  _[ ]  _[  ]       in bytes patterns or string patterns with the :[fn]ASCII:[-fn] flag.
  _[ ]  _[  ]       In string patterns without the :[fn]ASCII:[-fn] flag, it will match the
  _[ ]  _[  ]       range of Unicode alphanumeric characters (letters plus digits
  _[ ]  _[  ]       plus underscore). With :[fn]LOCALE:[-fn], it will match the set :[t][0-9_]:[-t] 
  _[ ]  _[  ]       plus characters defined as letters for the current locale.
  :[t]\W:[-t]       Matches the complement of :[t]\w:[-t].
  :[t]\\:[-t]       Matches a literal backslash.""",
        r""":[header]MODULE (re) FUNCTIONS:[-header]
  :[fn]match:[-fn]      Match a regular expression pattern to the beginning of a string.
  :[fn]fullmatch:[-fn]  Match a regular expression pattern to all of a string.
  :[fn]search:[-fn]     Search a string for the presence of a pattern.
  :[fn]sub:[-fn]        Substitute occurrences of a pattern found in a string.
  :[fn]subn:[-fn]       Same as sub, but also return the number of substitutions made.
  :[fn]split:[-fn]      Split a string by the occurrences of a pattern.
  :[fn]findall:[-fn]    Find all occurrences of a pattern in a string.
  :[fn]finditer:[-fn]   Return an iterator yielding a :[fn]Match:[-fn] object for each match.
  :[fn]compile:[-fn]    Compile a pattern into a :[fn]Pattern:[-fn] object.
  :[fn]purge:[-fn]      Clear the regular expression cache.
  :[fn]escape:[-fn]     Backslash all non-alphanumerics in a string.

  Each function other than :[fn]purge:[-fn] and :[fn]escape:[-fn] can take an optional :[hl]flags:[-hl] argument
  consisting of one or more of the following module constants, joined by :[t]|:[-t].""",
        r""":[header]FLAGS:[-header]
  :[fn]A:[-fn]  :[fn]ASCII:[-fn]       For string patterns, make :[|t]\w, \W, \b, \B, \d, \D:[-t] match
  _[  ] _[   ]  _[  ]     _[   ]       the corresponding :[fn]LOCALE:[-fn] character categories (rather
  _[  ] _[   ]  _[  ]     _[   ]       than the whole Unicode categories, which is the default).
  _[  ] _[   ]  _[  ]     _[   ]       For bytes patterns, this flag is the only available
  _[  ] _[   ]  _[  ]     _[   ]       behaviour and needn't be specified.
  :[fn]I:[-fn]  :[fn]IGNORECASE:[-fn]  Perform case-insensitive matching.
  :[fn]L:[-fn]  :[fn]LOCALE:[-fn]      Make :[|t]\w, \W, \b, \B:[-t] dependent on the current locale.
  :[fn]M:[-fn]  :[fn]MULTILINE:[-fn]   :[t]^:[-t] matches the beginning of lines (after a newline)
  _[  ] _[   ]  _[  ]         _[   ]   as well as the string.
  _[  ] _[   ]  _[  ]         _[   ]   :[t]$:[-t] matches the end of lines (before a newline) as well
  _[  ] _[   ]  _[  ]         _[   ]   as the end of the string.
  :[fn]S:[-fn]  :[fn]DOTALL:[-fn]      :[t].:[-t] matches any character at all, including the newline.
  :[fn]X:[-fn]  :[fn]VERBOSE:[-fn]     Ignore whitespace and comments for nicer looking RE's.
  :[fn]U:[-fn]  :[fn]UNICODE:[-fn]     For compatibility only. Ignored for string patterns (it
  _[  ] _[   ]  _[  ]       _[   ]     is the default), and forbidden for bytes patterns.

  :[|fn]A, L,:[-fn] and :[fn]U:[-fn] are mutually exclusive.
""",
    ]

    def __init__(self, ctx: click.Context, **kwargs):
        engine = pt.TemplateEngine(self.CUSTOM_STYLES)
        parsed_segs = [engine.parse(data_seg) for data_seg in self.DATA_SEGS]
        max_left_line_len = self._find_longest_line_len([parsed_segs[0], parsed_segs[2]])
        max_right_line_len = self._find_longest_line_len([parsed_segs[1], parsed_segs[3]])

        result = ""
        if pt.get_terminal_width() > max_left_line_len + max_right_line_len + self.PADDING:
            left_lines = "\n\n".join(
                get_stdout().render(" " + p) for p in [parsed_segs[0], parsed_segs[2]]
            ).splitlines()
            right_lines = "\n\n".join(
                get_stdout().render(p) for p in [parsed_segs[1], parsed_segs[3]]
            ).splitlines()
            left_justified = [pt.utilstr.ljust_sgr(ln, max_left_line_len) for ln in left_lines]
            for idx in range(0, max(len(left_justified), len(right_lines))):
                result += (
                    left_justified[idx]
                    if idx < len(left_justified)
                    else "".ljust(max_left_line_len)
                )
                result += " " * self.PADDING
                result += right_lines[idx] if idx < len(right_lines) else ""
                result += "\n"
        else:
            result += "\n\n".join(get_stdout().render(p) for p in parsed_segs)

        get_stdout().echo(result.rstrip())

    def _find_longest_line_len(self, segs: list[pt.Text]) -> int:
        result = 0
        for seg in segs:
            lines = ""
            for frag in seg._fragments:
                lines += frag.raw()
            for line in lines.splitlines():
                result = max(result, len(line))
        return result
