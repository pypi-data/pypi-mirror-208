# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from __future__ import annotations

import select
import subprocess
import typing as t
from subprocess import CompletedProcess, CalledProcessError

import pytermor as pt

from . import format_attrs
from .log import get_logger

args_filter = pt.NonPrintsStringVisualizer()


def run_detached(*args: t.Any) -> None:
    """
    Run subprocess in a shell,
    do not capture anything.
    """
    msg = f"Running detached: {format_attrs(map(args_filter.apply, args))}"
    get_logger().debug(msg)
    subprocess.run(*args, shell=True)


def run_subprocess(
    *args: t.Any,
    check: bool = True,
) -> CompletedProcess:
    """
    Run subprocess, wait for termination.
    Capture both stdout and stderr.
    """
    logger = get_logger()

    def log_streams_dump(out: t.Any, err: t.Any):
        for name, data in {"stdout": out, "stderr": err}.items():
            if data:
                logger.trace(data, name)
        logger.debug(f"Subprocess terminated")

    msg = f"Running subprocess: {format_attrs(map(args_filter.apply, args))}"
    logger.debug(msg)

    try:
        cp = subprocess.run(args, capture_output=True, encoding="utf8", check=check)
    except CalledProcessError as e:
        log_streams_dump(e.stdout.strip(), e.stdout.strip())
        raise e

    cp.stdout, cp.stderr = cp.stdout.strip(), cp.stderr.strip()
    log_streams_dump(cp.stdout, cp.stderr)
    return cp


def stream_subprocess(*args: t.Any) -> tuple[str | None, str | None]:
    """
    Run subprocess, yield stdout and stderr line by line.
    """
    logger = get_logger()
    logger.info(f"Starting subprocess piped: {format_attrs(map(args_filter.apply, args))}")

    process = subprocess.Popen(
        args, stderr=subprocess.PIPE, stdout=subprocess.PIPE, encoding="utf8"
    )
    logger.info(f"Started subprocess [{process.pid}]")

    for line in iter(process.stdout.readline, ""):
        logger.trace(line.rstrip(), f"[{process.pid} stdout]")
        yield line, None

    if err := process.stderr.read():
        for line in err.splitlines():
            logger.trace(line.rstrip(), f"[{process.pid} stderr]")
            yield None, line
    logger.debug(f"Subprocess [{process.pid}] closed streams")


def stream_pipe(cmd: str, timeout_sec: float = 0.001) -> t.Any:
    """
    Run subprocess, yield stdout.
    Wait no longer than ``timeout_sec`` before each iteration.
    """

    def read_pipe(stream: t.IO, stream_name: str) -> str:
        res = b""
        while select.select([stream.fileno()], [], [], timeout_sec)[0]:
            res += stream.read(1)
        if res:
            logger.trace(res.rstrip(), f"[{process.pid} {stream_name}]")
        return res.decode(errors="replace")

    logger = get_logger()
    process = subprocess.Popen(
        "/bin/sh",
        shell=False,
        bufsize=0,
        close_fds=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    logger.info(f"Opened shell pipe [{process.pid}]")

    while True:
        logger.debug(f"Invoking: {format_attrs(map(args_filter.apply, cmd))}")
        process.stdin.write(f"{cmd}\n".encode())

        while not select.select(
            [process.stdout.fileno(), process.stderr.fileno()], [], [], timeout_sec
        )[0]:
            pass
        if stdout_str := read_pipe(process.stdout, "stdout"):
            yield stdout_str
        if stderr_str := read_pipe(process.stderr, "stderr"):
            logger.error(f"Shell subprocess failure: {stderr_str}")
