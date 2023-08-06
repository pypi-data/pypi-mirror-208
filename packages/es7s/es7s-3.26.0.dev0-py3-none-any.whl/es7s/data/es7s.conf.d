######################################
#  DEFAULT es7s configuration file   #
#  DO NOT EDIT                       #
#  Run 'es7s config edit' to set up  #
######################################

[general]
syntax-version = 2.6
theme-color = blue


###  Data providers [es7s/daemon]  ###

[provider]
battery = on
cpu = on
disk = on
datetime = on
docker = on
fan = on
memory = on
network-country = on
network-latency = on
network-tunnel = on
shocks = on
temperature = on
timestamp = on
weather = on

[provider.network-latency]
host = 1.1.1.1
port = 53

[provider.shocks]
socks_protocol = socks5
socks_host = 127.0.0.1
socks_port = 1080
check_url = http://1.1.1.1

[provider.timestamp]
url = https://dlup.link/temp/nalog.mtime

[provider.weather]
location = MSK


###  Monitors [tmux]  ###

[monitor]
debug = off
force-cache = off

[monitor.combined]
layout1 =
    es7s.cli.monitor.SPACE
    es7s.cli.monitor.DiskUsageMonitor
    es7s.cli.monitor.MemoryMonitor
    es7s.cli.monitor.CpuLoadMonitor

    es7s.cli.monitor.EDGE_LEFT
    es7s.cli.monitor.SPACE
    es7s.cli.monitor.TemperatureMonitor
    es7s.cli.monitor.SPACE
    es7s.cli.monitor.DockerMonitor

    es7s.cli.monitor.SPACE
    es7s.cli.monitor.NetworkLatencyMonitor
    es7s.cli.monitor.SPACE
    es7s.cli.monitor.NetworkCountryMonitor
    es7s.cli.monitor.SPACE_2
    es7s.cli.monitor.NetworkTunnelMonitor
    es7s.cli.monitor.SPACE
    es7s.cli.monitor.TimestampMonitor
    es7s.cli.monitor.SPACE
    es7s.cli.monitor.WeatherMonitor

    es7s.cli.monitor.SPACE_2
    es7s.cli.monitor.DatetimeMonitor
    es7s.cli.monitor.SPACE_2
    es7s.cli.monitor.BatteryMonitor

layout2 =
    es7s.cli.monitor.EDGE_LEFT
    es7s.cli.monitor.CpuFreqMonitor
    es7s.cli.monitor.SPACE_2
    es7s.cli.monitor.CpuLoadAvgMonitor
    es7s.cli.monitor.SPACE
    es7s.cli.monitor.FanSpeedMonitor

[monitor.datetime]
display-year = off
display-seconds = off

[monitor.memory]
swap-warn-threshold = 0.7

[monitor.weather]
weather-icon-set-id = 0
weather-icon-max-width = 2
wind-speed-warn-threshold = 10.0


###  Indicators [gtk]  ###

[indicator]
debug = off
layout =
    es7s.gtk.IndicatorTimestamp
    es7s.gtk.IndicatorDiskUsage
    es7s.gtk.IndicatorMemory
    es7s.gtk.IndicatorCpuLoad
    es7s.gtk.IndicatorTemperature
    es7s.gtk.IndicatorShocks

[indicator.manager]
display = on
label-system-time = on
label-self-uptime = on
label-tick-nums = off
restart-timeout-min = 120

[indicator.disk]
display = on
label-used = off
label-free = off

[indicator.memory]
display = on
label-virtual-percents = off
label-virtual-bytes = off
label-swap-percents = off
label-swap-bytes = off
swap-warn-threshold = 0.7

[indicator.cpu-load]
display = on
label-current = off
label-average = off
label-average-3 = off

[indicator.timestamp]
display = on
label-value = off

[indicator.temperature]
; label = off|one|three
display = on
label = off

[indicator.shocks]
display = on
label = off
latency-warn-threshold-ms = 1000


###  Executables  ###

[exec.edit-image]
editor-raster = gimp
editor-vector = inkscape
ext-vector =
    svg

[exec.switch-wspace]
; indexes =
;    0
;    1
; filter = off|whitelist|blacklist
; selector = first|cycle
indexes =
filter = off
selector = first
