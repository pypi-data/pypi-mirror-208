# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from abc import abstractmethod, abstractproperty

import time
import typing as t
from dataclasses import dataclass, field

T = t.TypeVar("T")


def now() -> int:
    return int(time.time())


@dataclass(frozen=True)
class SocketMessage(t.Generic[T]):
    data: T
    timestamp: int = field(default_factory=now)
    network_comm: bool = False

    @property
    def data_hash(self) -> int:
        if isinstance(self.data, dict):
            return hash(frozenset(self.data.items()))
        return hash(self.data)


@dataclass(unsafe_hash=True)
class BatteryInfo:
    MAX_LEVEL = 100

    level: int | float = None
    is_charging: bool = None
    remaining_sec: int = None

    def __post_init__(self):
        self.level = max(0, min(self.MAX_LEVEL, self.level))

    @property
    def is_max(self) -> bool:
        return self.level is not None and round(self.level) >= self.MAX_LEVEL


@dataclass
class DockerStatus:
    match_amount: int = 0
    container_names: list[str] = field(default_factory=list)
    updated_in_prev_tick: bool = False

    def __hash__(self) -> int:
        return hash(
            frozenset([self.match_amount, self.updated_in_prev_tick, *self.container_names])
        )


@dataclass(frozen=True)
class WeatherInfo:
    location: str
    fields: list[str]

    def __hash__(self) -> int:
        return hash(frozenset([self.location, *self.fields]))


@dataclass(frozen=True)
class CpuInfo:
    freq_mhz: float = None
    load_perc: float = None
    load_avg: tuple[float, float, float] = None
    core_count: int = None
    thread_count: int = None


@dataclass(frozen=True)
class MemoryInfo:
    virtual_used: int = None
    virtual_total: int = None
    swap_used: int = None
    swap_total: int = None


@dataclass(frozen=True)
class TemperatureInfo:
    values_c: list[tuple[str, float]]

    def __hash__(self) -> int:
        return hash(frozenset(self.values_c))


@dataclass(frozen=True)
class FanInfo:
    values_rpm: list[int]

    def max(self) -> int:
        return max(self.values_rpm or [0])

    def __hash__(self) -> int:
        return hash(frozenset([self.max, *self.values_rpm]))


@dataclass(frozen=True)
class DiskUsageInfo:
    free: int
    total: int
    used_perc: float


@dataclass(frozen=True)
class NetworkCountryInfo:
    country: str = None
    ip: str = None
    mobile: bool = None
    proxy: bool = None
    hosting: bool = None


@dataclass(frozen=True)
class NetworkLatencyInfo:
    failed_ratio: float = None
    latency_s: float = None


@dataclass(frozen=True)
class NetworkTunnelInfo:
    amount: int = None


@dataclass(frozen=True)
class ShocksInfo:
    running: bool = None
    healthy: bool = None
    latency_s: float = None


@dataclass(frozen=True)
class TimestampInfo:
    ts: int = None
