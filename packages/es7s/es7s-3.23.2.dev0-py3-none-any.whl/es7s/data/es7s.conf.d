######################################
#  DEFAULT es7s configuration file   #
#  DO NOT EDIT                       #
#  Run 'es7s config edit' to set up  #
######################################

[general]
syntax-version = 2.5
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
    es7s.cli.monitor.combined.SPACE
    es7s.cli.monitor.disk_usage.DiskUsageMonitor
    es7s.cli.monitor.memory.MemoryMonitor
    es7s.cli.monitor.cpu_load.CpuLoadMonitor

    es7s.cli.monitor.combined.EDGE_LEFT
    es7s.cli.monitor.combined.SPACE
    es7s.cli.monitor.temperature.TemperatureMonitor
    es7s.cli.monitor.combined.SPACE
    es7s.cli.monitor.docker.DockerMonitor

    es7s.cli.monitor.combined.SPACE
    es7s.cli.monitor.network_latency.NetworkLatencyMonitor
    es7s.cli.monitor.combined.SPACE
    es7s.cli.monitor.network_country.NetworkCountryMonitor
    es7s.cli.monitor.combined.SPACE_2
    es7s.cli.monitor.network_tunnel.NetworkTunnelMonitor
    es7s.cli.monitor.combined.SPACE
    es7s.cli.monitor.timestamp.TimestampMonitor
    es7s.cli.monitor.combined.SPACE
    es7s.cli.monitor.weather.WeatherMonitor

    es7s.cli.monitor.combined.SPACE_2
    es7s.cli.monitor.datetime.DatetimeMonitor
    es7s.cli.monitor.combined.SPACE_2
    es7s.cli.monitor.battery.BatteryMonitor

layout2 =
    es7s.cli.monitor.combined.EDGE_LEFT
    es7s.cli.monitor.cpu_freq.CpuFreqMonitor
    es7s.cli.monitor.combined.SPACE_2
    es7s.cli.monitor.cpu_load_avg.CpuLoadAvgMonitor
    es7s.cli.monitor.combined.SPACE
    es7s.cli.monitor.fan_speed.FanSpeedMonitor

[monitor.datetime]
display-year = off
display-seconds = off

[monitor.memory]
swap-warn-threshold = 0.7

[monitor.weather]
weather-icon-set-id = 0
weather-icon-max-width = 2
wind-speed-warn-threshold = 10.0


###  Indicators [gnome-shell]  ###

[indicator]
debug = off
layout =
    es7s.gtk.indicator_timestamp.IndicatorTimestamp
    es7s.gtk.indicator_disk_usage.IndicatorDiskUsage
    es7s.gtk.indicator_memory.IndicatorMemory
    es7s.gtk.indicator_cpu_load.IndicatorCpuLoad
    es7s.gtk.indicator_temperature.IndicatorTemperature
    es7s.gtk.indicator_shocks.IndicatorShocks

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
