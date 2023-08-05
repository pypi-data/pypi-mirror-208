# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import threading as th
import time
import typing as t
from collections import deque

import requests

from ..shared import get_logger, ShutdownableThread, SocketServer, get_config
from ..shared.threads import ThreadSafeCounter, class_to_command_name

T = t.TypeVar("T")


class DataProvider(ShutdownableThread, t.Generic[T]):
    _network_request_id = ThreadSafeCounter()

    def __init__(self, config_var: str | None, socket_topic: str, poll_interval_sec=1.0):
        self._config_var = config_var
        self._socket_topic = socket_topic
        self._poll_interval_sec = poll_interval_sec

        pvname = class_to_command_name(self) + "-pv"
        super().__init__(command_name=pvname, thread_name="collect")

        self._daemon_buf = deque[any](maxlen=1)
        self._network_req_event = th.Event()

        if not self._is_enabled():
            self.shutdown()
            self.start()
            return

        self._socket_server = SocketServer(
            self._daemon_buf,
            self._socket_topic,
            pvname,
            self._network_req_event,
        )
        self._socket_server.start()
        self.start()

    def run(self):
        super().run()
        logger = get_logger()
        wait_sec = 0

        while True:
            if self.is_shutting_down():
                self.destroy()
                break

            if 0 < wait_sec <= 1:
                time.sleep(wait_sec)
            elif wait_sec > 1:
                time.sleep(1)
                wait_sec -= 1
                continue

            data = None
            try:
                data = self._collect()
                logger.debug(f"Collected data {data}")
                self._daemon_buf.append(data)
            except DataCollectionError as e:
                logger.error(e.msg)
            except Exception as e:
                logger.exception(e)

            if not data:
                if data := self._reset():
                    self._daemon_buf.append(data)

            wait_sec = self._poll_interval_sec

    def _is_enabled(self) -> bool:
        return get_config().getboolean("provider", self._config_var, fallback=False)

    def _reset(self) -> T | None:
        pass

    def _collect(self) -> T:
        raise NotImplementedError()

    def _get_request_timeout(self) -> float:
        return max(1.0, self._poll_interval_sec / 2)

    def _make_request(
        self,
        url: str,
        request_fn: t.Callable[[], requests.Response] = None,
        log_response_body: bool = True,
    ) -> requests.Response:
        logger = get_logger()
        try:
            request_id = self._network_request_id.next()
            self._network_req_event.set()
            logger.log_http_request(request_id, url)
            if not request_fn:
                request_fn = lambda: requests.get(url, timeout=self._get_request_timeout())
            response = request_fn()
            logger.log_http_response(request_id, response, with_body=log_response_body)
        except requests.exceptions.ConnectionError as e:
            logger.error(e)
            raise DataCollectionError()
        except requests.RequestException as e:
            logger.exception(e)
            raise DataCollectionError()
        finally:
            self._network_req_event.clear()

        if not response.ok:
            logger.warning(f"Weather fetching failed: HTTP {response.status_code}")
            raise DataCollectionError()

        logger.trace(response.text, "Remote service response")
        return response


class DataCollectionError(Exception):
    def __init__(self, msg: str = "Data collection failed"):
        self._msg = msg

    @property
    def msg(self) -> str:
        return self._msg
