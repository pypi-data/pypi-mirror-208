# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
# PyGTK is pain in the ass.
# There is not a day goes by I don't feel regret
# for my decision to implement OS-level indicators.
import gi

# try which gir is available prioritising Gtk3
gi.require_version("AppIndicator3", "0.1")
try:
    from gi.repository import AyatanaAppIndicator3 as AppIndicator
except ImportError:
    try:
        from gi.repository import AppIndicator3 as AppIndicator
    except ImportError:
        from gi.repository import AppIndicator as AppIndicator  # noqa

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk as Gtk, GLib as GLib

# ------------------------------------------------------------------------------
# here imports should be absolute:
from es7s.gtk._entrypoint import invoke as entrypoint_fn

from .indicator_cpu_load import IndicatorCpuLoad as IndicatorCpuLoad
from .indicator_disk_usage import IndicatorDiskUsage as IndicatorDiskUsage
from .indicator_manager import IndicatorManager as IndicatorManager
from .indicator_memory import IndicatorMemory as IndicatorMemory
from .indicator_shocks import IndicatorShocks as IndicatorShocks
from .indicator_temperature import IndicatorTemperature as IndicatorTemperature
from .indicator_timestamp import IndicatorTimestamp as IndicatorTimestamp
