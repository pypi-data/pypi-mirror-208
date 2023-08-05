# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
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
