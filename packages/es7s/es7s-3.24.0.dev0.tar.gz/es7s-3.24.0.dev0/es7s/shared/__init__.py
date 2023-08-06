# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

from .color import get_color
from .config import (
    ConfigLoaderParams,
    get_config,
    get_default_config,
    init_config,
    reset_config,
    save_config,
    get_user_config_filepath,
)
from .dto import SocketMessage, BatteryInfo, DockerStatus, WeatherInfo
from .io import (
    IoParams,
    IoProxy,
    get_stdout,
    get_stderr,
    init_io,
    destroy_io,
)
from .ipc import SocketServer, SocketClient
from .log import (
    LoggerParams,
    Logger,
    get_logger,
    init_logger,
    destroy_logger,
    format_attrs,
)
from .styles import Styles, FrozenStyle
from .threads import (
    ShutdownableThread,
    shutdown as shutdown_threads,
    shutdown_started,
)
from .prefixed_unit import DemoText
from .sub import run_subprocess, stream_subprocess, stream_pipe
from .separator import UNIT_SEPARATOR
from .spinner import SpinnerBrailleSquareCenter
from .sun_calc import SunCalc
from .weather_icons import justify_wicon, get_wicon
