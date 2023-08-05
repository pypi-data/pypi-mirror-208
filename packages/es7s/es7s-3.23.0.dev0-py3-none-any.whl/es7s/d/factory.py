# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from ._base import DataProvider
from .provider_battery import BatteryProvider
from .provider_cpu import CpuProvider
from .provider_datetime import DatetimeProvider
from .provider_disk_usage import DiskUsageProvider
from .provider_docker import DockerStatusProvider
from .provider_fan_speed import FanSpeedProvider
from .provider_memory import MemoryProvider
from .provider_network_country import NetworkCountryProvider
from .provider_network_latency import NetworkLatencyProvider
from .provider_network_tunnel import NetworkTunnelProvider
from .provider_shocks import ShocksProvider
from .provider_temperature import TemperatureProvider
from .provider_timestamp import TimestampProvider
from .provider_weather import WeatherProvider


class DataProviderFactory:
    @classmethod
    def make_providers(cls) -> list[DataProvider]:
        return [
            BatteryProvider(),
            CpuProvider(),
            DiskUsageProvider(),
            DockerStatusProvider(),
            FanSpeedProvider(),
            MemoryProvider(),
            NetworkCountryProvider(),
            NetworkLatencyProvider(),
            NetworkTunnelProvider(),
            ShocksProvider(),
            DatetimeProvider(),
            TemperatureProvider(),
            TimestampProvider(),
            WeatherProvider(),
        ]
