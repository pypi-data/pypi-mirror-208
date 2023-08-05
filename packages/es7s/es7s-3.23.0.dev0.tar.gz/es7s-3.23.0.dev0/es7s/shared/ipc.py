# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import os.path
import pickle
import socket as s
import threading as th
from abc import ABCMeta, abstractmethod
from collections import deque

import time

from . import threads
from .dto import T, SocketMessage
from .log import get_logger
from .system import get_socket_path


class SocketServer(threads.ShutdownableThread):
    LISTEN_TIMEOUT_SEC = 1

    def __init__(
        self,
        daemon_buf: deque[any],
        socket_path_suffix: str,
        provider_name: str,
        network_req_event: th.Event,
    ):
        # setting daemon to True so that the main process doesn't wait for this thread to terminate
        super().__init__(command_name=provider_name, thread_name="socksend", daemon=True)

        self._daemon_buf = daemon_buf
        self._socket_path = get_socket_path(socket_path_suffix, write=True)
        self._network_req_event = network_req_event
        self._unlink_socket_path()

        get_logger().debug(f"Binding to {self._socket_path}")
        self._socket = s.socket(s.AF_UNIX, s.SOCK_STREAM)
        self._socket.bind(self._socket_path)
        self._socket.settimeout(self.LISTEN_TIMEOUT_SEC)

    def run(self):
        get_logger().info(f'Starting {self} at: "{self._socket_path}"')

        logger = get_logger()
        self._socket.listen()

        while True:
            if self.is_shutting_down():
                self.destroy()
                break

            try:
                conn, _ = self._socket.accept()
            except TimeoutError:
                continue

            try:
                data = self._daemon_buf[0]
                msg = SocketMessage[T](data, network_comm=self._network_req_event.is_set())
                logger.debug(f"Composed msg {msg}")

                serialized_msg = pickle.dumps(msg, protocol=pickle.HIGHEST_PROTOCOL)
                logger.debug(f"Writing {len(serialized_msg)} bytes to daemon buffer")
                logger.trace(serialized_msg)
                conn.send(serialized_msg)
            except BrokenPipeError:
                pass
            except IndexError:
                # let the client log this, will be significantly
                # less spam errors in syslog
                pass
            except Exception as e:
                logger.exception(e)
            finally:
                conn.close()

    def destroy(self):
        super().destroy()
        try:
            self._socket.close()
        except Exception as e:
            get_logger(False).exception(e)
        self._unlink_socket_path()

    def _unlink_socket_path(self):
        try:
            os.unlink(self._socket_path)
        except OSError:
            if os.path.exists(self._socket_path):
                raise


class IClientIPC(metaclass=ABCMeta):
    @abstractmethod
    def start(self):
        ...

    @abstractmethod
    def shutdown(self):
        ...


class NullClient(IClientIPC):
    def start(self):
        pass

    def shutdown(self):
        pass


class SocketClient(threads.ShutdownableThread, IClientIPC):
    RECV_CHUNK_SIZE = 1024

    def __init__(
        self,
        monitor_data_buf: deque[bytes],
        eff_recv_interval_sec: float,
        pause_event: th.Event,
        ready_event: th.Event,
        socket_topic: str,
        command_name: str,
    ):
        # setting daemon to True so that the main process doesn't wait for this thread to terminate
        super().__init__(command_name=command_name, thread_name="sockrecv", daemon=True)

        self._monitor_data_buf = monitor_data_buf
        self._eff_recv_interval_sec = eff_recv_interval_sec
        self._pause_event = pause_event
        self._ready_event = ready_event
        self._socket_path = get_socket_path(socket_topic)
        self._socket = None

    def run(self):
        get_logger().info(f'Starting {self} at: "{self._socket_path}"')
        logger = get_logger()
        recv_interval_sec = 0.1  # first one only

        while True:
            if self.is_shutting_down():
                self.destroy()
                break
            if self._pause_event.is_set():
                time.sleep(1)
                continue

            try:
                self._socket = s.socket(s.AF_UNIX, s.SOCK_STREAM)
                self._socket.connect(self._socket_path)
            except (ConnectionRefusedError, FileNotFoundError) as e:
                logger.error(f"Unable to connect to {self._socket_path}: {e}")
            except Exception as e:
                logger.exception(e)
            else:
                if data := self._socket.recv(self.RECV_CHUNK_SIZE):
                    self._monitor_data_buf.append(data)
                    if not self._ready_event.is_set():
                        self._ready_event.set()
                        logger.debug("Received first message from daemon")
                    logger.debug(f"Received {len(data)} bytes of data")
                self._socket.close()
            time.sleep(recv_interval_sec)
            recv_interval_sec = self._eff_recv_interval_sec

    def destroy(self):
        super().destroy()
        try:
            self._socket.close()
        except Exception as e:
            get_logger(False).exception(e)
