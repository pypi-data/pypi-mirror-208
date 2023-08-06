# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import os
import pydoc
import signal
import sys
import typing

from . import Gtk
from ._base import _BaseIndicator
from .indicator_manager import IndicatorManager
from .. import APP_VERBOSITY
from ..shared import (
    get_stdout,
    init_logger,
    LoggerParams,
    init_io,
    IoParams,
    init_config,
    get_stderr,
)
from ..shared.config import ConfigLoaderParams, get_config
from ..shared.threads import exit_gracefully


def invoke():
    os.environ.update({"ES7S_DOMAIN": "GTK"})
    _init()
    try:
        ic = IndicatorController()
        ic.run()
    except SystemExit:
        if stdout := get_stdout(False):
            stdout.echo()
        raise


def _init():
    logger_params = LoggerParams(verbosity=APP_VERBOSITY)
    io_params = IoParams()

    logger = init_logger(params=logger_params)
    _, _ = init_io(io_params)
    init_config(ConfigLoaderParams())

    logger.log_init_params(
        ("Log configuration:", logger_params),
        ("Logger setup:", {"handlers": logger.handlers}),
        ("IO configuration:", io_params),
        ("Stdout proxy setup:", get_stdout().as_dict()),
        ("Stderr proxy setup:", get_stderr().as_dict()),
    )


class IndicatorController:
    def __init__(self):
        signal.signal(signal.SIGUSR1, self._exit)
        signal.signal(signal.SIGINT, self._exit)
        signal.signal(signal.SIGTERM, self._exit)

        self._indicators: list[_BaseIndicator] = []
        self._indicator_mgr: IndicatorManager|None = None

    def run(self):
        self._init_threads()
        Gtk.main()
        for indicator in self._indicators:
            indicator.join()

    def _init_threads(self):
        self._indicators = [*IndicatorFactory().make_from_config()]
        self._indicator_mgr = IndicatorManager(indicators=self._indicators)
        self._indicators.insert(0, self._indicator_mgr)

    def _exit(self, signal_code: int, *args):
        exit_gracefully(signal_code, callback=None)
        Gtk.main_quit()
        sys.exit(signal_code)


class IndicatorFactory:
    def make_from_config(self) -> typing.Iterable[_BaseIndicator]:
        config = get_config()
        layout_cfg = filter(None, config.get("indicator", "layout").strip().split("\n"))

        for el in reversed([*layout_cfg]):
            module_name, origin_name = el.rsplit(".", 1)
            if (module := pydoc.safeimport(module_name)) is None:
                continue

            origin: type = getattr(module, origin_name)
            yield origin()
