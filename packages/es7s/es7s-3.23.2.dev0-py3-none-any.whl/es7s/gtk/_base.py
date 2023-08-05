# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import os
import pickle
import threading as th
import time
import typing as t
from abc import ABC, abstractmethod
from collections import deque, OrderedDict
from dataclasses import dataclass
from typing import ClassVar

import pkg_resources

from . import AppIndicator, gi
from .. import APP_NAME
from ..shared import ShutdownableThread, SocketClient, get_logger, SocketMessage, get_config, \
    save_config
from ..shared.ipc import IClientIPC
from ..shared.path import RESOURCE_DIR

DT = t.TypeVar("DT")


class IndicatorUnboundState:
    abs_running_time_sec: float = 0
    tick_update_num: int = 0
    tick_render_num: int = 0
    timeout: int = 0
    wait_timeout: int = 0

    def __repr__(self):
        parts = (
            f"Å={self.abs_running_time_sec:.1f}",
            f"U={self.tick_update_num}",
            f"R={self.tick_render_num}",
            f"T={self.timeout:.1f}",
            f"W={self.wait_timeout:.1f}",
        )
        return f"{self.__class__.__qualname__}[{' '.join(parts)}]"

    @property
    def warning_switch(self) -> bool:
        return self.tick_update_num % 2 == 0

    @property
    def is_waiting(self) -> bool:
        return self.wait_timeout > 0

    def cancel_wait(self):
        self.wait_timeout = 0

    def log(self):
        get_logger().trace(repr(self), "State")


@dataclass
class _State:
    active = False
    gobject: gi.repository.Gtk.MenuItem = None

    @abstractmethod
    def click(self):
        ...


@dataclass
class _StaticState(_State):
    callback: t.Callable[[_State], None] = None

    def click(self):
        if self.callback:
            self.callback(self)


@dataclass
class _BoolState(_StaticState):
    value: bool = True
    config_var: tuple[str, str] = None  # (section, name)
    config_var_value: str = None  # for radios
    gobject: gi.repository.Gtk.CheckMenuItem | gi.repository.Gtk.RadioMenuItem = None

    def __post_init__(self):
        if self.config_var is not None:
            if self.config_var_value is None:
                self.value = get_config().getboolean(*self.config_var)
            else:
                self.value = (get_config().get(*self.config_var) == self.config_var_value)

    def __bool__(self):
        return self.value

    @property
    def active(self) -> bool:
        return self.value

    def click(self):
        self.value = not self.value
        self._update_config(self.value)
        super().click()

    def update_title(self, title: str):
        if not self.gobject:
            return
        self.gobject.set_title(title)

    def activate(self):
        if self.value:
            return
        self.gobject.set_active(True)

    def deactivate(self):
        if not self.value:
            return
        self.gobject.set_active(False)

    def _update_config(self, val: bool):
        if self.config_var is not None:
            if self.config_var_value is None:
                get_config().set(*self.config_var, 'on' if val else 'off')
            else:
                if not val:
                    return
                get_config().set(*self.config_var, self.config_var_value)
            save_config()


@dataclass(frozen=True)
class MenuItemConfig:
    label: str
    sensitive: bool = True
    separator_before: bool = False

    def make(self, state: _State) -> gi.repository.Gtk.MenuItem:
        return gi.repository.Gtk.MenuItem.new_with_label(self.label)


@dataclass(frozen=True)
class CheckMenuItemConfig(MenuItemConfig):
    def make(self, state: _BoolState) -> gi.repository.Gtk.MenuItem:
        item = gi.repository.Gtk.CheckMenuItem.new_with_label(self.label)
        item.set_active(state.active)
        item.set_sensitive(self.sensitive)
        return item


@dataclass(frozen=True)
class RadioMenuItemConfig(MenuItemConfig):
    last_item: ClassVar["RadioMenuItemConfig"] = None

    def make(self, state: _BoolState) -> gi.repository.Gtk.MenuItem:
        item = gi.repository.Gtk.RadioMenuItem.new_with_label([], self.label)
        gi.repository.Gtk.RadioMenuItem.join_group(item, RadioMenuItemConfig.last_item)
        item.set_active(state.active)
        RadioMenuItemConfig.last_item = item
        return item


class _BaseIndicator(ShutdownableThread, t.Generic[DT], ABC):
    TICK_DURATION_SEC = 0.5

    SOCKRCV_INTERVAL_SEC = 1.0
    RENDER_INTERVAL_SEC = 2.0
    RENDER_ERROR_TIMEOUT_SEC = 5.0
    ICONS_PATH = "icons-v13"

    def __new__(cls, *args, **kwargs):
        inst = super().__new__(cls)
        inst._action_queue = deque()
        inst.config_section = None
        return inst

    def __init__(
        self,
        indicator_name: str,
        socket_topic: str = None,
        icon_name_default: str = None,
        icon_path_dynamic_tpl: str = None,
        icon_thresholds: list[int] = None,
        title: str = None,
    ):
        super().__init__(command_name=indicator_name, thread_name="ui")

        self._monitor_data_buf = deque[bytes](maxlen=1)
        self._socket_client_pause = th.Event()
        self._socket_client_ready = th.Event()
        self._socket_client = self._make_socket_client(
            socket_topic=socket_topic or indicator_name,
            indicator_name=indicator_name,
        )

        self._theme_path = pkg_resources.resource_filename(APP_NAME, os.path.join(RESOURCE_DIR, self.ICONS_PATH))
        self._icon_name_default = icon_name_default
        self._icon_path_dynamic_tpl = icon_path_dynamic_tpl
        self._icon_thresholds = icon_thresholds
        self.title = title

        self.public_hidden_state = th.Event()  # костыль
        config_val = get_config().getboolean(self.config_section, "display")
        if not config_val:
            self.public_hidden_state.set()
        self._hidden = _BoolState(value=not config_val, callback=self._update_visibility)

        self._state_map = OrderedDict[MenuItemConfig, _State]()
        self._state_map.update(
            {
                CheckMenuItemConfig(
                    title or indicator_name,
                    sensitive=False,
                    separator_before=True,
                ): _StaticState()
            }
        )
        # self._state_map.update({CheckMenuItemConfig("Hide", separator_before=False): self._hidden})
        self._init_state()

        self._indicator: AppIndicator.Indicator = AppIndicator.Indicator.new(
            f"es7s-indicator-{indicator_name}",
            self._icon_name_default or "apport-symbolic",
            AppIndicator.IndicatorCategory.HARDWARE,
        )
        # ---------------------------↓--@debug-----------------------------
        def dbg(*args):
            get_logger().warning("CONNECTED: %s" % args[0].get_property("connected"))
            get_logger().info( "\n".join(str(a) for a in args))
        for ev in ["connection-changed"]:
            self._indicator.connect(ev, dbg)
        get_logger().info("CONNECTED: %s" % self._indicator.get_property("connected"))
        # ---------------------------↑--@debug-----------------------------
        self._indicator.set_attention_icon("dialog-warning")
        self._indicator.set_icon_theme_path(self._theme_path)

        self._menu = gi.repository.Gtk.Menu()
        self._init_menu()
        self._menu.show()
        self._indicator.set_menu(self._menu)
        self._update_visibility()

        self._socket_client.start()
        self.start()

    def _make_socket_client(self, socket_topic: str, indicator_name: str) -> IClientIPC:
        return SocketClient(
            self._monitor_data_buf,
            eff_recv_interval_sec=self.SOCKRCV_INTERVAL_SEC,
            pause_event=self._socket_client_pause,
            ready_event=self._socket_client_ready,
            socket_topic=socket_topic,
            command_name=indicator_name,
        )

    def _init_state(self):
        self._state = IndicatorUnboundState()

    def _init_menu(self):
        for config, state in self._state_map.items():
            self._make_menu_item(config, state)

    def shutdown(self):
        super().shutdown()
        self._socket_client.shutdown()
        self._menu.hide()

    def _enqueue(self, fn: callable):
        self._action_queue.append(fn)

    def _make_menu_item(
        self, config: MenuItemConfig, state: _State = None
    ) -> gi.repository.Gtk.CheckMenuItem:
        if config.separator_before:
            sep = gi.repository.Gtk.SeparatorMenuItem.new()
            sep.show()
            self._menu.append(sep)

        item = config.make(state)
        item.connect("activate", lambda c=config: self._click_menu_item(config))
        item.show()
        self._menu.append(item)
        state.gobject = item

        return item

    def _click_menu_item(self, config: MenuItemConfig):
        if (state := self._state_map.get(config)) is not None:
            state.click()

    def _update_visibility(self, _: _State = None):
        if self._hidden:
            self._indicator.set_status(AppIndicator.IndicatorStatus.PASSIVE)
            self.public_hidden_state.set()
        else:
            self._indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
            self.public_hidden_state.clear()

    def run(self):
        super().run()
        self._socket_client_ready.wait(self.TICK_DURATION_SEC)

        while True:
            self._on_before_update()
            if self.is_shutting_down():
                self.destroy()
                break
            if self._state.timeout > self.TICK_DURATION_SEC:
                self._sleep(self.TICK_DURATION_SEC)
                continue
            self._sleep(self._state.timeout)

            if self.public_hidden_state.is_set() != self._hidden.value:
                self._hidden.click()

            try:
                act = self._action_queue.popleft()
            except IndexError:
                act = self._update
            act()

    def _sleep(self, timeout_sec: float):
        if timeout_sec == 0:
            return

        time.sleep(timeout_sec)
        self._state.abs_running_time_sec += timeout_sec
        self._state.timeout = max(0.0, self._state.timeout - timeout_sec)
        self._state.wait_timeout = max(0.0, self._state.wait_timeout - timeout_sec)
        self._state.log()

    def _add_timeout(self, timeout_sec: float = None):
        self._state.timeout += timeout_sec or self.RENDER_INTERVAL_SEC

    def _on_before_update(self):
        pass

    def _update(self):
        logger = get_logger()

        self._state.tick_update_num += 1
        try:
            try:
                msg_raw = self._monitor_data_buf[0]
            except IndexError:
                logger.warning("No data from daemon")
                self._add_timeout()
                self._render_no_data()
                return

            msg = self._deserialize(msg_raw)

            # msg_ttl = self._setup.message_ttl
            msg_ttl = 5.0  # @TODO
            now = time.time()

            if now - msg.timestamp > msg_ttl:
                self._monitor_data_buf.remove(msg_raw)
                raise RuntimeError(f"Expired socket message: {now} > {msg.timestamp}")

            else:
                # logger.trace(msg_raw, label="Received data dump")
                logger.debug("Deserialized changed message: " + repr(msg))
                self._add_timeout()
                self._state.tick_render_num += 1
                self._render(msg)

        except Exception as e:
            logger.exception(e)
            self._add_timeout(self.RENDER_ERROR_TIMEOUT_SEC)
            self._render_error()

    def _deserialize(self, msg_raw: bytes) -> SocketMessage[DT]:
        msg = pickle.loads(msg_raw)
        return msg

    def _select_icon(self, carrier_value: float) -> str:
        if not self._icon_thresholds or not self._icon_path_dynamic_tpl:
            return self._icon_name_default

        icon_subtype = self._icon_thresholds[-1]
        for thr in self._icon_thresholds:
            icon_subtype = thr
            if carrier_value >= thr:
                break
        return self._icon_path_dynamic_tpl % icon_subtype

    @abstractmethod
    def _render(self, msg: SocketMessage[DT]):
        ...

    def _render_no_data(self):
        self._set("...", None, AppIndicator.IndicatorStatus.ACTIVE)

    def _render_result(
        self, result: str, guide: str = None, warning: bool = False, icon: str = None
    ):
        status = AppIndicator.IndicatorStatus.ACTIVE
        if warning and self._state.warning_switch:
            status = AppIndicator.IndicatorStatus.ATTENTION
        self._set(result, guide, status)

        if icon:
            get_logger().trace(icon, "SET Icon")
            self._indicator.set_icon_full(os.path.join(self._theme_path, icon), icon)

    def _render_error(self):
        self._set("ERR", None, AppIndicator.IndicatorStatus.ATTENTION)

    def _set(self, label: str, guide: str | None, status: AppIndicator.IndicatorStatus):
        if self._hidden:
            return
        logger = get_logger()
        logger.trace(label, "SET Label")
        logger.trace(status.value_name, "SET Status")

        if get_config().get_indicator_debug_mode():
            label = label.replace(" ", "␣")
        self._indicator.set_label(label, guide or label)
        self._indicator.set_status(status)
