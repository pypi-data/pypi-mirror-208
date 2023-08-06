# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import enum
import os
import re
import stat
import typing as t

import click
from click import IntRange

from es7s import APP_NAME
from .._base_opts_params import EnumChoice, EpilogPart, CMDTYPE_BUILTIN, CMDTRAIT_X11
from .._decorators import cli_pass_context, _catch_and_log_and_exit, cli_option, cli_command, \
    cli_argument
from ...shared import get_config, get_logger, run_subprocess, format_attrs
from ...shared.path import WMCTRL_PATH, USER_ES7S_BIN_DIR, RESOURCE_DIR


class FilterType(str, enum.Enum):  # @TODO str enums will be available in python 3.11
    OFF = "off"
    WHITELIST = "whitelist"
    BLACKLIST = "blacklist"

    def __str__(self):
        return self.value


class SelectorType(str, enum.Enum):  # @TODO str enums will be available in python 3.11
    FIRST = "first"
    CYCLE = "cycle"

    def __str__(self):
        return self.value


@cli_command(
    name=__file__,
    short_help="switch between workspaces",
    type=CMDTYPE_BUILTIN,
    traits=[CMDTRAIT_X11],
    epilog=[
        EpilogPart(
            "<indexes>=` 0 1 `   <filter>=`whitelist`   <selector>=`first`   workspaces:{0}1 2",
            title="Workflow examples:",
            group="1",
        ),
        EpilogPart("< >", group="1"),
        EpilogPart(
            "  After hitting the keystroke exclude active workspace from overall list "
            "=> 1 2, apply the whitelist => 1, and switch to the only one available "
            "left, which is *1*. /*This example together with the next one illustrate "
            "how the workspaces can be toggled between each other using one and the "
            "same key combination.*/",
            group="1",
        ),
        EpilogPart(
            "<indexes>=` 0 1 `   <filter>=`whitelist`   <selector>=`first`   workspaces: 0{1}2",
            group="2",
        ),
        EpilogPart("< >", group="2"),
        EpilogPart(
            "  Exclude active from overall => 0 2, apply the whitelist => 0, "
            "and switch to the only one available workspace left, which is *0*. "
            "/*As you can see, this setup implements switching between workspaces "
            "0 and 1, while 2 is ignored.*/",
            group="2",
        ),
        EpilogPart(
            "<indexes>=` 3 `   <filter>=`blacklist`   <selector>=`cycle`   workspaces: 0{1}2 3 4",
            group="3",
        ),
        EpilogPart("< >", group="3"),
        EpilogPart(
            "  Exclude active first => get 0 2 3 4, then subtract blacklisted "
            "and get 0 2 4, then find the leftmost available workspace relative to the "
            "place where our active workspace was originally located, which is *2*."
            "/* The next invocation results in *4*, the one after that -- in *0*, and "
            "so the selector will make one full cycle and can start the next one. */",
            group="3",
        ),
    ],
)
@cli_argument(
    "indexes",
    type=IntRange(0, max_open=True),
    nargs=-1,
)
@cli_option(
    "-f",
    "--filter",
    type=EnumChoice(FilterType),
    default=lambda: get_config().get("exec.switch-wspace", "filter"),
    help="Name of the filter method to apply to the list of target workspace indexes. If omitted,  "
    "read it from config.",
)
@cli_option(
    "-s",
    "--selector",
    type=EnumChoice(SelectorType),
    default=lambda: get_config().get("exec.switch-wspace", "selector"),
    help="Name of the selector method used to choose the final workspace to switch to if there "
    "is more than 1 of them. If omitted, read it from config.",
)
@cli_option(
    "-n",
    "--dry-run",
    is_flag=True,
    default=False,
    help="Don't actually switch to other workspace, just pretend to "
    "(suggestion: can be used with '-vv' for debugging).",
)
@cli_option(
    "-S",
    "--shell",
    is_flag=True,
    default=False,
    help="Instead of normal execution create or refresh shell script with hardcoded "
         "current configuration on-board (the values from config can be rewritten "
         "with command args and persist in the shell script till next script update). "
         "Shall be used for invocations instead of calling slow general-purpose 'es7s' "
         "CLI entrypoint (x10 speed boost, from 250ms to 25ms). Optimized entrypoint "
         "is located in @USER_ES7S_BIN_DIR@ environment variable and should be "
         "called directly: 'switch-wspace-turbo'.",
)
@cli_pass_context
@_catch_and_log_and_exit
class SwitchWorkspaceCommand:
    """
    Switch the current workspace to the next available one. Convenient for a
    situations when you want to have a keystroke to switch the workspaces
    back and forth, but do not want to keep several different key combos for each
    workspace and will be satisfied with just one keystroke that can cycle through
    specified workspace indexes. The algorithm is:\n\n

    - Get current workspace list from the OS, exclude the active workspace from it.\n\n

    - Apply the specified *filter* method to current workspace list with the *INDEXES* arguments
    as filter operands. In case the filter method is `blacklist`, exclude the *INDEXES* from
    current workspace list. In case of `whitelist` keep indexes that are present in
    INDEXES list and throw away all the others. Do not perform a filtration if method is set
    to `off`. Note that INDEXES arguments are optional and if the list is omitted, it will be
    read from the config instead.\n\n

    - Pick suitable index from filtered list using *selector* method. In case it is `first`,
    just return the very first element of the list (i.e., the lowest index). In case it is
    `cycle`, the result workspace will be the leftmost workspace in the filtered list after
    the current one, or first if there are none such a workspaces.\n\n

    - Switch the current workspace to the one selected in previous step.\n\n

    This command requires ++/bin/wmctrl++ to be present and available.
    """

    def __init__(
        self,
        ctx: click.Context,
        indexes: t.Sequence[int],
        filter: FilterType,
        selector: SelectorType,
        shell: bool,
        dry_run: bool,
        **kwargs,
    ):
        self._config_section = f"exec.{ctx.command.name}"

        filter_idxs = set(indexes)
        if len(filter_idxs) == 0:
            filter_idxs = set(get_config().getintlist(self._config_section, "indexes"))

        if shell:
            self._update_shell_script(filter_idxs, filter, selector, dry_run)
        else:
            self._run(filter_idxs, filter, selector, dry_run)

    def _update_shell_script(
        self,
        filter_idxs: set[int],
        filter_type: FilterType,
        selector_type: SelectorType,
        dry_run: bool,
    ):
        import pkg_resources
        logger = get_logger()

        filter_regex = '^$'
        if len(filter_idxs) > 0:
            filter_regex = '|'.join(map(str, filter_idxs))

        tpl = pkg_resources.resource_string(
            APP_NAME,
            os.path.join(RESOURCE_DIR, "switch-wspace-turbo.tpl")
        ).decode()
        tpl_params = {
            'filter_name': filter_type.value,
            'filter_regex': filter_regex,
            'selector_name': selector_type.value,
            'wmctrl_path': WMCTRL_PATH,
        }
        logger.debug(f"Substitution values: {format_attrs(tpl_params)}")

        script = tpl % tpl_params
        logger.debug(f"Template length: {len(tpl)}")
        logger.debug(f"Script length: {len(script)}")

        script_path = os.path.join(USER_ES7S_BIN_DIR, 'switch-wspace-turbo')

        msg = f'Writing the result script: {script_path}'
        if dry_run:
            logger.info(f"[DRY-RUN] {msg}")
            return  # @TODO notice instead, the difference is that it's going to stderr even at -v 0
        logger.info(msg)

        with open(script_path, "wt") as f:
            f.write(script)

        st = os.stat(script_path)
        logger.debug(f'Setting the "+executable" flag')
        os.chmod(script_path, st.st_mode | stat.S_IEXEC)

    def _run(
        self,
        filter_idxs: set[int],
        filter_type: FilterType,
        selector_type: SelectorType,
        dry_run: bool,
    ):
        logger = get_logger()

        allowed_idxs = []
        active_idx = None

        for wspace_str in self._get_wspace_list():
            if (m := re.search(r"^(\d+)\s*([*-]).+$", wspace_str)) is None:
                continue

            idx = int(m.group(1))
            if m.group(2) == "*":
                active_idx = idx
                logger.debug(f"Workspace {idx}: DENIED (current active)")
                continue

            if not self._is_allowed_by_filter(idx, filter_idxs, filter_type):
                continue

            logger.debug(f"Workspace {idx}: ALLOWED")
            allowed_idxs.append(idx)

        logger.debug(
            f"Allowed target workspaces ({len(allowed_idxs)}): " + format_attrs(allowed_idxs)
        )
        if active_idx is None:
            logger.warning("Failed to determine active workspace")

        if len(allowed_idxs) == 0:
            logger.info("No allowed target workspaces found")
            return

        target_idx = self._select(allowed_idxs, active_idx, selector_type)
        logger.debug(f"Target workspace: {target_idx}")

        if dry_run:
            logger.info(f"[DRY-RUN] Switching workspace to {target_idx}")
            return
        self._switch_to_wspace(target_idx)

    def _get_wspace_list(self) -> list[str]:
        return run_subprocess(WMCTRL_PATH, "-d").stdout.splitlines()

    def _is_allowed_by_filter(
        self, idx: int, filter_idxs: set[int], filter_type: FilterType
    ) -> bool:
        if filter_type == FilterType.OFF:
            return True

        if filter_type == FilterType.BLACKLIST:
            return idx not in filter_idxs

        if filter_type == FilterType.WHITELIST:
            return idx in filter_idxs

        raise RuntimeError(f"Invalid filter: {filter_type}")

    def _select(self, allowed_idxs: list[int], active_idx: int, selector_type: SelectorType) -> int:
        if selector_type == SelectorType.FIRST:
            return allowed_idxs[0]
        if selector_type == SelectorType.CYCLE:
            allowed_next_to_active_idxs = [*filter(lambda idx: idx > active_idx, allowed_idxs)]
            if len(allowed_next_to_active_idxs) == 0:
                return allowed_idxs[0]
            return allowed_next_to_active_idxs[0]
        raise RuntimeError(f"Invalid selector: {selector_type}")

    def _switch_to_wspace(self, target_idx):
        run_subprocess(WMCTRL_PATH, f"-s{target_idx}")
