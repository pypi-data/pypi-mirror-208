# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import sys
import typing as t
import pytermor as pt

from es7s.shared import IoProxy, get_stdout, get_logger


class TerminalStateController:
    def __init__(self, io_proxy: IoProxy = None):
        self._io_proxy: IoProxy = io_proxy or get_stdout()
        self._restore_callbacks: list[t.Callable[[], None]] = []
        self._terminal_orig_settings: list | None = None

    def enable_alt_screen_buffer(self):
        self._add_restore_callback(self._disable_alt_screen_buffer)
        self._add_restore_callback(self._restore_cursor_position)
        self._send_sequence(pt.make_save_cursor_position)

        get_logger().debug(
            f"TSC: ENABLING ALT SCREEN BUFFER: all stderr log messages are now IGNORED "
            f"by the terminal; syslog logging still works if enabled"
        )
        self._send_sequence(pt.make_enable_alt_screen_buffer)

    def hide_cursor(self):
        self._add_restore_callback(self._show_cursor)
        self._send_sequence(pt.make_hide_cursor)

    def disable_input(self):
        get_logger().debug(f"TSC: Putting tty into cbreak mode: {sys.stdin}")
        if not self._ensure_tty():
            return

        import tty
        import termios

        self._add_restore_callback(self._restore_input)
        self._terminal_orig_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin)

    def restore_state(self):
        get_logger().debug(f"TSC: Restoring state ({len(self._restore_callbacks)})")
        while self._restore_callbacks:
            self._restore_callbacks.pop()()

    def _disable_alt_screen_buffer(self):
        self._send_sequence(pt.make_disable_alt_screen_buffer)
        get_logger().debug(
            f"TSC: DISABLED ALT SCREEN BUFFER: stderr logging should work again"
        )

    def _restore_cursor_position(self):
        self._send_sequence(pt.make_restore_cursor_position)

    def _show_cursor(self):
        self._send_sequence(pt.make_show_cursor)

    def _restore_input(self):
        if not self._ensure_tty():
            return

        get_logger().debug(f"TSC: Restoring tty attributes: {self._terminal_orig_settings}")

        import termios

        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._terminal_orig_settings)

    def _add_restore_callback(self, fn: t.Callable[[], None]) -> None:
        get_logger().debug(f"TSC: Registering callback: '{fn.__name__}'")
        self._restore_callbacks.append(fn)

    def _send_sequence(self, fn: t.Callable[[], pt.ISequence]) -> None:
        if not self._ensure_tty():
            return

        sequence = fn()
        get_logger().debug(f"TSC: Sending control sequence: '{fn.__name__}' -> '{sequence!r}'")
        self._io_proxy.echo(sequence)

    def _ensure_tty(self):
        if not self._io_proxy.io.isatty():
            get_logger().debug(f"TSC: Ignoring directive as output device is not a tty")
            return False
        return  True
