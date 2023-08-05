# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import socket
import struct

import requests

from ._base import DataProvider
from ..shared import get_logger, get_config
from ..shared.dto import ShocksInfo


class ShocksProvider(DataProvider[ShocksInfo]):
    def __init__(self):
        super().__init__("shocks", "shocks", 11.0)

    def _reset(self):
        return ShocksInfo()

    def _collect(self) -> ShocksInfo:
        config = get_config()
        config_section = "provider." + self._config_var

        socks_protocol = config.get(config_section, "socks_protocol")
        socks_host = config.get(config_section, "socks_host")
        socks_port = config.getint(config_section, "socks_port")
        socks_url = f"{socks_protocol}://{socks_host}:{socks_port}"
        check_url = config.get(config_section, "check_url")

        if not self._check_proxy_is_up(socks_host, socks_port):
            return ShocksInfo()

        try:
            response = self._check_can_connect(socks_url, check_url)
        except Exception as e:
            get_logger().error(f"Connectivity error: {e}")
        else:
            if response.ok:
                return ShocksInfo(
                    running=True,
                    healthy=True,
                    latency_s=response.elapsed.total_seconds(),
                )
            get_logger().error(f"Connectivity error: {response.text}")

        return ShocksInfo(running=True)

    def _check_proxy_is_up(self, socks_host: str, socks_port: int) -> bool:
        sen = struct.pack("BBB", 0x05, 0x01, 0x00)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        msg_tpl = f"Socks proxy {socks_host}:{socks_port} is %s"
        try:
            s.connect((socks_host, socks_port))
            s.sendall(sen)
            s.recv(2)
            # data = s.recv(2)
            # version, auth = struct.unpack('BB', data)
            s.close()
        except IOError | OSError as e:
            get_logger().debug(msg_tpl % f"down: {e}")
            return False
        get_logger().debug(msg_tpl % "up")
        return True

    def _check_can_connect(self, socks_url: str, check_url: str) -> requests.Response:
        return self._make_request(
            check_url,
            request_fn=lambda: requests.get(
                check_url,
                timeout=self._get_request_timeout(),
                proxies={"http": socks_url, "https": socks_url},
            ),
            log_response_body=False,
        )
