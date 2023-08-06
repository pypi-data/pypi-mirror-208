# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import math
import pathlib
import typing
from datetime import datetime
from os import stat_result
from stat import filemode
from time import sleep

import pytermor as pt

from es7s.shared import get_stdout, FrozenStyle, get_logger
from es7s.shared.progress_bar import ProgressBar
from es7s.shared.strutil import fit
from .._base_opts_params import IntRange
from .._decorators import (
    cli_argument,
    cli_command,
    cli_option,
    _catch_and_log_and_exit,
    _preserve_terminal_state,
    _with_progress_bar,
)


@cli_command(__file__, help="Launch a demonstration of ProgressBar CLI component.")
@cli_option(
    "-s",
    "--slower",
    default=1,
    help="Add an artificial delay of eⁿ seconds between operations."
    " By default (n=0) no delay is applied. n=1 sets the delay to ≈3ms, "
    "n=5 to ≈140ms, n=10 to ≈21sec. Reasonable slow levels "
    "are within range [1;5], others make the execution process look "
    "like step debugging.",
    type=IntRange(_min=0, _max=10),
)
@cli_option(
    "-f",
    "--faster",
    default=False,
    is_flag=True,
    help="Override any delays set by '--slower' option and furthermore "
    "speed up the execution by disabling file headers reading.",
)
@cli_argument("path", default="/home", type=pathlib.Path)
@_catch_and_log_and_exit
@_preserve_terminal_state
@_with_progress_bar
class DemoProgressBarCommand:
    """ """

    def __init__(self, pbar: ProgressBar, path: pathlib.Path, slower: int, faster: bool, **kwargs):
        self._path = path
        self._slower = slower
        self._faster = faster
        if self._faster:
            self._slower = 0

        self.run(pbar)

    def run(self, pbar: ProgressBar):
        pathes = [*filter(lambda f: f.is_dir(), self._path.iterdir())]

        stdout = get_stdout()
        pbar.setup(len(pathes))

        table = pt.SimpleTable()

        idx_pt = 0
        for pidx, path in enumerate(pathes):
            pbar.next_threshold(label_thr=path.absolute().name)
            try:
                children: typing.Sequence[pathlib.Path] = [*path.iterdir()]
            except:
                continue

            for idx, child in enumerate(sorted(children)):
                idx_pt += 1
                pbar.set(ratio_local=idx / len(children), label_local=str(child))
                data = b""
                st: stat_result | None = None
                try:
                    st: stat_result = child.stat()
                    if child.is_file() and not self._faster:
                        data = child.open("rb").read(12)
                except FileNotFoundError as e:
                    get_logger().warning(e)
                    # stdout.echo_rendered(
                    #     pt.FrozenText(
                    #         pt.Fragment(" ! ", FrozenStyle(fg="yellow", bold=True)),
                    #         pt.Fragment(f"{e}"),
                    #     )
                    # )
                except Exception as e:
                    get_logger().error(e)
                    # stdout.echo_rendered(
                    #     pt.FrozenText(
                    #         pt.Fragment(
                    #             " × ", FrozenStyle(bg="dark red", fg="bright white", bold=True)
                    #         ),
                    #         pt.Fragment(f" {e}", "red"),
                    #     )
                    # )
                    continue
                if not st:
                    continue

                cc = ""
                for c in data:
                    cc += hex(c).removeprefix("0x").zfill(2) + " "
                while len(cc) < 12 * 3:
                    cc += "·· "
                if self._slower:
                    sleep(math.e**self._slower / 1000)

                row = table.pass_row(
                    pt.Fragment(fit(str(idx_pt), 5, ">"), FrozenStyle(dim=True)),
                    pt.Fragment("|", "blue"),
                    pt.Text(str(child.resolve()), overflow="…"),
                    pt.FrozenText(pt.format_bytes_human(st.st_size), width=8, align=">"),
                    pt.FrozenText(filemode(st.st_mode), width=12, align=">"),
                    pt.FrozenText(
                        datetime.fromtimestamp(st.st_mtime).strftime("%_e-%b-%Y"),
                        width=12,
                        align=">",
                    ),
                    pt.Fragment("|", "blue"),
                    pt.Fragment(cc),
                    renderer=stdout.renderer,
                )
                get_stdout().echo(row)
            pbar.set(finished=True)
        get_logger().info(f" ⏺  " + "Did a lot of hard (fake) work: WIN")
        # stdout.echo(stdout.render()
