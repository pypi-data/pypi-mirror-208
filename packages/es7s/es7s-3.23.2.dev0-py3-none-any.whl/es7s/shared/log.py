# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2021-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from __future__ import annotations

import logging
import os
import pathlib
import re
import sys
import threading
import typing as t
from dataclasses import dataclass
from logging import (
    Logger as BaseLogger,
    LogRecord as BaseLogRecord,
    StreamHandler,
    handlers,
    DEBUG,
    INFO,
    WARNING,
    ERROR,
    CRITICAL,
    Formatter,
)

import click
import pytermor as pt

from .. import APP_NAME, APP_VERSION, APP_DAEMON_DEBUG
from .io import get_stderr
from .styles import Styles

TRACE = 5
logging.addLevelName(TRACE, "TRACE")

VERBOSITY_TO_LOG_LEVEL_MAP = {
    0: [WARNING, INFO],
    1: [INFO, DEBUG],
    2: [DEBUG, TRACE],
    3: [TRACE, TRACE],
}


@dataclass
class LoggerParams:
    verbosity: int = 0
    quiet: bool = False
    out_stderr: bool = True
    out_syslog: bool = True
    out_file: str | None = None

    @property
    def trace(self) -> bool:
        return self.verbosity >= 2


def get_logger(require=True) -> Logger | DummyLogger:
    if logger := Logger.get_instance(require):
        return logger
    return DummyLogger()


def init_logger(app_name="es7s", ident_part="core", params=LoggerParams()) -> Logger:
    return Logger(app_name, ident_part, params)


def destroy_logger():
    Logger.destroy()


class DummyLogger:
    quiet = False

    def log(self, *args, **kwargs):
        print(str(*args, **kwargs))

    debug = log
    info = log
    warning = log
    error = log


class Logger(BaseLogger):
    _logger: Logger | None = None

    @classmethod
    def get_instance(cls, require: bool) -> Logger | DummyLogger | None:
        if not cls._logger:
            if require:
                raise RuntimeError("Logger is uninitialized")
            return None
        return cls._logger

    @classmethod
    def destroy(cls):
        cls._logger = None

    @property
    def verbosity_allows_monitor_debugging_markup(self) -> bool:
        return self.verbosity > 0

    @property
    def verbosity_allows_progress_bar_mode(self) -> bool:
        return self.verbosity == 0 or self.verbosity >= 3

    HTTP_RESPONSE_FILTERS = [
        pt.utilstr.StringLinearizer(),
    ]
    TRACE_EXTRA_FILTERS: t.List[pt.utilstr.IFilter] = [
        pt.SgrStringReplacer(),
        pt.StringMapper({ord("\n"): " "}),
        pt.OmniSanitizer(),
    ]

    def __init__(self, app_name: str, ident_part: str, params: LoggerParams):
        """
        :param app_name:
        :param ident_part:
        :param params:
        """
        super().__init__(app_name)
        Logger._logger = self

        stderr_level, syslog_level = VERBOSITY_TO_LOG_LEVEL_MAP[
            min(len(VERBOSITY_TO_LOG_LEVEL_MAP) - 1, params.verbosity)
        ]
        file_level = syslog_level
        self.setLevel(min(stderr_level, syslog_level))
        self.verbosity = params.verbosity
        self.quiet = params.quiet

        self._stderr_handler = None
        self._sys_log_handler = None
        self._file_handler = None
        if not self.quiet and params.out_stderr:
            self._stderr_formatter = _StderrFormatter(params, external=False)
            self._stderr_handler = _StderrHandler(stream=sys.stderr)
            self._stderr_handler.setLevel(stderr_level)
            self._stderr_handler.setFormatter(self._stderr_formatter)
            self.addHandler(self._stderr_handler)

        if params.out_syslog:
            sys_log_handler = _SysLogHandler(ident=f"{app_name}/{ident_part}")
            try:
                sys_log_handler.ensure_available()
            except (FileNotFoundError, RuntimeError):
                pass
            else:
                self._sys_log_handler = sys_log_handler
                self._sys_log_handler.setLevel(syslog_level)
                self._sys_log_handler.setFormatter(_SyslogFormatter())
                self.addHandler(self._sys_log_handler)

        if params.out_file:
            self._file_handler = _FileHandler(params.out_file, "a")
            self._file_handler.setLevel(file_level)
            self._file_handler.setFormatter(_FileFormatter())
            self.addHandler(self._file_handler)

        self.log_init_info()

        if os.environ.get('PYTERMOR_TRACE_RENDERS'):
            self._init_pytermor_logging(stderr_level, params)

    def _init_pytermor_logging(self, level: int, params: LoggerParams):
        pt_stderr_handler = StreamHandler(stream=sys.stderr)
        pt_stderr_handler.setLevel(level)
        pt_stderr_handler.setFormatter(_StderrFormatter(params, external=True))
        logger = logging.getLogger("pytermor")
        logger.handlers.clear()
        logger.addHandler(pt_stderr_handler)
        logger.setLevel(level)
        pt.init_config()

    def update_default_streams(self, stderr: t.IO):
        if self._stderr_handler:
            self._stderr_handler.setStream(stderr)

    def exception(self, msg: object, **kwargs):
        msg = f"{msg.__class__.__qualname__}: {msg!s}"
        super().exception(msg)

    def log_http_request(self, req_id: int | str, url: str, method: str = "GET"):
        self.info(f"[#{req_id}] > {method} {url}")

    def log_http_response(self, req_id: int | str, response: 'requests.Response', with_body: bool):
        msg_resp = f"[#{req_id}] < HTTP {response.status_code}"
        msg_resp += ", " + pt.format_si(response.elapsed.total_seconds(), "s")
        msg_resp += ", " + pt.format_si_binary(len(response.text))
        if with_body:
            msg_resp += ': "'
            msg_resp += pt.apply_filters(response.text, *self.HTTP_RESPONSE_FILTERS)
            msg_resp += '"'
        self.info(msg_resp)

    def log_init_info(self):
        appver = f"{APP_NAME} {os.getenv('ES7S_DOMAIN')} v{APP_VERSION} "
        appver += "[debug]" if APP_DAEMON_DEBUG else ""
        self.info(appver)
        self.info(
            format_attrs(
                {
                    "PID": os.getpid(),
                    "PPID": os.getppid(),
                    "UID": os.getuid(),
                    "CWD": os.getcwd(),
                }
            )
        )

    def log_init_params(self, *params_desc: tuple[str, object]):
        for (label, params) in params_desc:
            params_str = format_attrs(params, keep_classname=False) if params else ""
            self.debug(label.ljust(20) + params_str)

    def trace(
        self,
        data: str | bytes,
        label: str = None,
        out_plain: bool = True,
        out_sanitized: bool = False,
        out_ucp: bool = False,
        out_utf8: bool = False,
        out_hex: bool = False,
    ):
        if not data:
            return
        label = (f"{label.upper()} " if label else "")
        dump = []

        if not isinstance(data, (str, bytes)):
            data = str(data)

        if isinstance(data, str):
            if out_plain:
                dump += [data]
            if out_sanitized:
                dump += [pt.apply_filters(data, *self.TRACE_EXTRA_FILTERS)]
            if out_ucp:
                dump += [pt.utilstr.dump(data, "", 32)]
            if out_utf8:
                dump += [pt.StringTracer().apply(data)]
        else:
            if out_hex:
                dump += [pt.BytesTracer().apply(data)]

        if len(dump) == 0:
            return

        if len(dump) > 1 or "\n" in dump[0]:
            dump.insert(0, label + "::")
        else:
            dump[0] = label + ": " + dump[0]

        self.log(TRACE, "\n".join(dump))

    def makeRecord(
        self,
        name: str,
        level: int,
        fn: str,
        lno: int,
        msg: object,
        args: t.Any,
        exc_info: t.Any,
        func: str | None = ...,
        extra: t.Mapping[str, object] | None = ...,
        sinfo: str | None = ...,
    ) -> LogRecord:
        if not isinstance(extra, dict):
            extra = {}
        rv = LogRecord(name, level, fn, lno, msg, args, exc_info, func, sinfo, **extra)
        return rv


class LogRecord(BaseLogRecord):
    def __init__(
        self,
        name: str,
        level: int,
        pathname: str,
        lineno: int,
        msg: object,
        args: t.Any,
        exc_info: t.Any,
        func: str | None = ...,
        sinfo: str | None = ...,
        pid=None,
        stream=None,
    ) -> None:
        super().__init__(name, level, pathname, lineno, msg, args, exc_info, func, sinfo)
        domain = os.getenv("ES7S_DOMAIN")

        source_1 = domain.upper() if domain else (self.name + "." + self.module)
        self.source = "[" + source_1 + "]"
        if source_2 := self._get_command_name():
            self.source += "[" + re.sub(r"[^a-zA-Z0-9.:-]+", "", source_2[:24]) + "]"

        self.pid = pid
        self.stream = stream

        self.sep_stream = ""
        if self.stream:
            if self.pid:
                self.sep_stream = f"[{self.pid} {self.stream.upper()}]"
            else:
                self.sep_stream = f"[{self.stream.upper()}]"

        self.rel_created_str = pt.format_time_delta(self.relativeCreated / 1000, 6)

    def _get_command_name(self) -> str | None:
        name = None
        if ctx := click.get_current_context(silent=True):
            name = ctx.command.name
        if thread := threading.current_thread():
            if not name or thread != threading.current_thread():
                name = thread.name
        return name


class GenericHandler(logging.Handler):
    def __repr__(self):
        return f"{self.__class__.__qualname__}[{logging.getLevelName(self.level)}]"


class _StderrHandler(GenericHandler, StreamHandler):
    def handle(self, record: LogRecord):
        super().handle(record)
        # reset cached exc_text after _Es7sStderrFormatter
        # so that syslog won't receive SGRs
        record.exc_text = None


class _FileHandler(GenericHandler, logging.FileHandler):
    pass


class _SysLogHandler(GenericHandler, handlers.SysLogHandler):
    level_overrides = {
        "TRACE": "DEBUG",
    }

    def __init__(
        self,
        ident: str,
        address: str = "/dev/log",
        facility: int = handlers.SysLogHandler.LOG_LOCAL7,
        **kwargs,
    ):
        super().__init__(address=address, facility=facility, **kwargs)
        self.ident = f"{ident}[{os.getpid()}]: "

    def ensure_available(self):
        if not os.path.exists(self.address):
            raise FileNotFoundError(self.address)
        if not pathlib.Path(self.address).is_socket():
            raise RuntimeError(f"Syslog receiver is found, but is not a socket: {self.address}")

    def mapPriority(self, levelName):
        levelName = self.level_overrides.get(levelName, levelName)
        return super().mapPriority(levelName)


class _SyslogFormatter(Formatter):
    def __init__(self, **kwargs) -> None:
        super().__init__(
            fmt=f"%(source)s%(sep_stream)s(+%(rel_created_str)s) %(message)s", **kwargs
        )


class _FileFormatter(Formatter):
    def __init__(self, **kwargs) -> None:
        super().__init__(
            fmt=f"[%(asctime)s]%(source)s%(sep_stream)s(+%(rel_created_str)s) %(message)s", **kwargs
        )


class _StderrFormatter(Formatter):
    STYLE_DEFAULT = pt.NOOP_STYLE
    STYLE_EXCEPTION = pt.Styles.ERROR

    LEVEL_TO_STYLE_MAP = {
        CRITICAL: pt.Styles.CRITICAL,
        ERROR: pt.Styles.ERROR_ACCENT,
        WARNING: pt.Styles.WARNING,
        INFO: pt.Style(fg=pt.cv.WHITE),
        DEBUG: Styles.STDERR_DEBUG,
        TRACE: Styles.STDERR_TRACE,
    }

    FORMAT_DEFAULT = "%(levelname)s: %(message)s"
    FORMAT_VERBOSE = "[%(levelname)-5.5s]%(source)s%(sep_stream)s(+%(rel_created_str)s) %(message)s"
    FORMAT_EXTERNAL = f"[%(levelname)-5.5s][ - ][%(name)s.%(module)s] %(message)s"

    def __init__(self, params: LoggerParams, external: bool, **kwargs):
        fmt = self.FORMAT_DEFAULT
        if params.verbosity > 0:
            fmt = self.FORMAT_VERBOSE
        if external:
            fmt = self.FORMAT_EXTERNAL
        super().__init__(fmt=fmt, **kwargs)

        self._show_exc_info = params.verbosity > 0

    def formatMessage(self, record: LogRecord) -> str:
        formatted_msg = super().formatMessage(record)
        msg_style = self._resolve_style(record.levelno)
        return self._render_or_raw(formatted_msg, msg_style)

    def formatException(self, ei):
        if not self._show_exc_info:
            return None
        formatted = super().formatException(ei)
        result = "\n".join(
            self._render_or_raw(line, self.STYLE_EXCEPTION)
            for line in formatted.splitlines(keepends=False)
        )
        return result

    def _render_or_raw(self, msg, style):
        if stderr := get_stderr(False):
            return stderr.render(msg, style)
        return msg

    def _resolve_style(self, log_level: int | t.Literal) -> pt.Style:
        return self.LEVEL_TO_STYLE_MAP.get(log_level, self.STYLE_DEFAULT)


def format_attrs(*o: object, keep_classname: bool = True, level: int = 0) -> str:
    def to_str(a) -> str:
        if (s := str(a)).startswith(cn := a.__class__.__name__):
            if keep_classname:
                return s
            return s.removeprefix(cn)
        return f"'{s}'" if s.count(" ") else s

    if len(o) == 1:
        o = o[0]
    if isinstance(o, str):
        return o
    elif isinstance(o, t.Mapping):
        return "(" + " ".join(f"{to_str(k)}={format_attrs(v)}" for k, v in o.items()) + ")"
    elif isinstance(o, t.Iterable):
        return "(" + " ".join(format_attrs(v, level=level + 1) for v in o) + ")"
    return to_str(o)


# resulting syslog output (partial):

# _TRANSPORT=syslog             # logs filtering:
# PRIORITY=7                    #
# SYSLOG_FACILITY=23            #    "journalctl --facility=local7" (all es7s logs are sent to this facility)
# _UID=1001                     # or "journalctl --ident=es7s/corectl" (that's "syslog_ident" argument)
# _GID=1001                     # or "journalctl --grep MONITOR:docker" (filter by group or/and command)
# _EXE=/usr/bin/python3.10
# _CMDLINE=/home/a.shavykin/.local/pipx/venvs/es7s/bin/python /home/a.shavykin/.local/bin/es7s corectl install
# _COMM=es7s
# SYSLOG_PID=846461
# SYSLOG_IDENTIFIER=es7s/corectl
# MESSAGE=[MONITOR:docker] Initialized with (verbose=0 quiet=False c=False color=None) [log.py:92]
