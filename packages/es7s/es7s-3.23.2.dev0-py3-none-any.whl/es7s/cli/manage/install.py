# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2021-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import math
import os
import shutil
from time import sleep

import pytermor as pt

from es7s import APP_NAME
from es7s.shared import get_logger, get_stdout
from es7s.shared.path import RESOURCE_DIR, USER_ES7S_BIN_DIR, USER_ES7S_DATA_DIR
from es7s.shared.progress_bar import ProgressBar
from .._decorators import (
    _catch_and_log_and_exit,
    cli_option,
    cli_command,
    _with_progress_bar,
    _preserve_terminal_state,
)


@cli_command(__file__)
@cli_option(
    "-n",
    "--dry-run",
    is_flag=True,
    default=False,
    help="Don't actually do anything, just pretend to.",
)
@cli_option(
    "-s",
    "--symlinks",
    is_flag=True,
    default=False,
    help="Make symlinks to core files instead of copying them. "
    "Useful for es7s development, otherwise unnecessary.",
)
@_catch_and_log_and_exit
@_preserve_terminal_state
@_with_progress_bar
class InstallCommand:
    """Install es7s system."""

    def __init__(
        self,
        pbar: ProgressBar,
        dry_run: bool,
        symlinks: bool,
        **kwargs,
    ):
        self._dry_run = dry_run
        self._symlinks = symlinks

        self._stages = {
            self._run_prepare: "Preparing",
            self._run_copy_core: "Copying core files",
            self._run_inject_bashrc: "Injecting into shell",
            self._run_inject_gitconfig: "Injecting git config",
            self._run_copy_data: "Copying data",
            self._run_copy_bin: "Copying executables",
            self._run_install_with_apt: "Installing apt packages",
            self._run_install_with_pip: "Installing pip packages",
            self._run_install_x11: "Installing X11 packages",
            self._run_dload_install: "Downloading packages directly",
            self._run_build_install_tmux: "Building/installing tmux",
            self._run_build_install_less: "Building/installing less",
            self._run_install_es7s_exts: "Installing es7s extensions",
            self._run_install_daemon: "Installing es7s/daemon",
            self._run_install_shocks_service: "Installing es7s/shocks",
            self._run_setup_cron: "Setting up cron",
        }
        self._current_stage: str | None = None
        self._pbar = pbar

        self._run()

    def _run(self):
        self._pbar.setup(len(self._stages))
        for stage_fn, stage_desc in self._stages.items():
            self._current_stage = stage_fn.__qualname__.split(".")[1].lstrip("_")
            self._pbar.next_threshold(stage_desc)
            self._log(f"Starting stage: {self._current_stage}")
            try:
                stage_fn()
            except Exception as e:
                raise RuntimeError(self._current_stage + " failed") from e

    def _run_prepare(self):
        # install docker
        # sudo xargs -n1 <<< "docker syslog adm sudo" adduser $(id -nu)
        # ln -s /usr/bin/python3 ~/.local/bin/python
        pass

    def _run_copy_core(self):
        # install i -cp -v
        # git+ssh://git@github.com/delameter/pytermor@2.1.0-dev9
        pass

    def _run_inject_bashrc(self):
        pass

    def _run_inject_gitconfig(self):
        pass

    def _run_copy_data(self):
        import pkg_resources

        count = 0

        dist_dir_relpath = os.path.join(RESOURCE_DIR)
        dist_dir = pkg_resources.resource_listdir(APP_NAME, dist_dir_relpath)

        if os.path.exists(USER_ES7S_DATA_DIR):
            if not self._remove_file_or_dir(USER_ES7S_DATA_DIR):
                raise RuntimeError(f"Failed to remove dir, aborting", [USER_ES7S_DATA_DIR])

        if not self._make_dir(USER_ES7S_DATA_DIR):
            raise RuntimeError(f"Failed to create dir, aborting", [USER_ES7S_DATA_DIR])

        total = len(dist_dir)
        for idx, dist_relpath in enumerate(dist_dir):
            self._pbar.set(idx / total, label_local=dist_relpath)

            dist_abspath = pkg_resources.resource_filename(
                APP_NAME, os.path.join(dist_dir_relpath, dist_relpath)
            )
            if not os.path.isfile(dist_abspath):
                continue
            user_abspath = os.path.join(USER_ES7S_DATA_DIR, os.path.basename(dist_relpath))

            if not self._copy_or_symlink(dist_abspath, user_abspath):
                raise RuntimeError(f"Failed to copy file, aborting", [dist_abspath])
            count += 1

        self._echo_success(f"Installed {count} data files")

    def _run_copy_bin(self):
        import pkg_resources

        logger = get_logger()
        count = 0

        dist_dir_relpath = os.path.join(RESOURCE_DIR, "bin")
        dist_dir = pkg_resources.resource_listdir(APP_NAME, dist_dir_relpath)

        if not os.path.exists(USER_ES7S_BIN_DIR):
            if not self._make_dir(USER_ES7S_BIN_DIR):
                raise RuntimeError(f"Failed to create dir, aborting", [USER_ES7S_BIN_DIR])

        total = len(dist_dir)
        for idx, dist_relpath in enumerate(dist_dir):
            self._pbar.set(idx / total, label_local=dist_relpath)

            dist_abspath = pkg_resources.resource_filename(
                APP_NAME, os.path.join(dist_dir_relpath, dist_relpath)
            )
            user_abspath = os.path.join(USER_ES7S_BIN_DIR, os.path.basename(dist_relpath))

            if os.path.exists(user_abspath) or os.path.islink(user_abspath):  # may be broken link
                if not self._remove_file_or_dir(user_abspath):
                    logger.warning(f"Failed to remove file: '{user_abspath}', skipping...")
                    continue

            if not self._copy_or_symlink(dist_abspath, user_abspath):
                raise RuntimeError(f"Failed to copy file, aborting", [dist_abspath])
            count += 1

        self._echo_success(f"Installed {count} bin files")

    def _run_install_with_apt(self):
        pass

    def _run_install_with_pip(self):
        pass

    def _run_install_x11(self):
        pass

    def _run_dload_install(self):
        # ginstall exa
        # ginstall bat
        pass

    def _run_build_install_tmux(self):
        # install tmux deps
        # build_tmux
        # ln -s `pwd`/tmux ~/bin/es7s/tmux
        # git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
        # tmux run-shell /home/delameter/.tmux/plugins/tpm/bindings/install_plugins
        pass

    def _run_build_install_less(self):
        # install less deps
        # build_less
        pass

    def _run_install_es7s_exts(self):
        # install i -i -v

        # colors
        # fonts?
        # > pipx install kolombos
        # leo
        # > pipx install macedon
        # watson
        # nalog
        pass

    def _run_install_daemon(self):
        # copy es7s.service to /etc/systemd/system
        # replace USER placeholders
        # enable es7s, reload systemd
        pass

    def _run_install_shocks_service(self):
        # copy es7s-shocks.service to /etc/systemd/system
        # replace USER placeholders
        # enable shocks, reload systemd
        pass

    def _run_setup_cron(self):
        pass

    # -------------------------------------------------

    def _make_dir(self, user_path: str) -> bool:
        self._log_io("Creating", user_path)
        if self._dry_run:
            return True

        try:
            os.makedirs(user_path)
            self._log_io("Created", user_path)
        except Exception as e:
            get_logger().exception(e)
            return False

        return os.path.exists(user_path)

    def _remove_file_or_dir(self, user_path: str) -> bool:
        self._log_io("Removing", user_path)
        if self._dry_run:
            return True

        try:
            if os.path.isfile(user_path) or os.path.islink(user_path):
                os.unlink(user_path)
                self._log_io("Removed", user_path)
            elif os.path.isdir(user_path):
                shutil.rmtree(user_path)
                self._log_io("Removed", user_path)
            else:
                self._log_io("Not found", user_path)

        except Exception as e:
            get_logger().exception(e)
            return False

        return not os.path.exists(user_path)

    def _copy_or_symlink(self, dist_path: str, user_path: str) -> bool:
        action = "Linking" if self._symlinks else "Copying"

        self._log_io(action, user_path, dist_path)
        if self._dry_run:
            return True

        try:
            if self._symlinks:
                os.symlink(dist_path, user_path)
                self._log_io("Linked", user_path, dist_path)
            else:
                shutil.copy(dist_path, user_path)
                self._log_io("Copied", user_path, dist_path)

        except Exception as e:
            get_logger().exception(e)
            return False

        return True

    def _log_io(self, action: str, target: str, source: str = None):
        prefix = ""
        path = f'"{target}"'
        if source:
            path = f'"{source}" -> {path}'
        self._log(f"{prefix}{action+':':<9s} {path}")

    def _log(self, msg: str):
        prefix = ""
        if self._dry_run:
            prefix += "DRY-RUN|"
        prefix += self._current_stage
        get_logger().info(f"[{prefix}] {msg}")

    def _echo_success(self, msg: str):
        if self._dry_run:
            msg += " [NOT REALLY]"
        self._log(msg)

        stdout = get_stdout()
        msg = stdout.render(" ⏺ ", pt.cv.GREEN) + msg
        stdout.echo(msg)
