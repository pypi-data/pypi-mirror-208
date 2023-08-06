# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from ._base import _BaseIndicator, _BoolState, RadioMenuItemConfig
from ..shared import SocketMessage
from ..shared.dto import TemperatureInfo


class IndicatorTemperature(_BaseIndicator[TemperatureInfo]):
    def __init__(self):
        self.config_section = "indicator.temperature"

        self._show_none = _BoolState(
            config_var=(self.config_section, "label"),
            config_var_value="off",
        )
        self._show_one = _BoolState(
            config_var=(self.config_section, "label"),
            config_var_value="one",
        )
        self._show_three = _BoolState(
            config_var=(self.config_section, "label"),
            config_var_value="three",
        )

        super().__init__(
            "temperature",
            icon_name_default="temperature-0.svg",
            icon_path_dynamic_tpl="temperature-%d.svg",
            icon_thresholds=[
                90,
                80,
                70,
                50,
                30,
                10,
                0,
            ],
            title="Thermal sensors",
        )

    def _init_state(self):
        super()._init_state()
        self._state_map.update(
            {
                RadioMenuItemConfig("No label", separator_before=True): self._show_none,
                RadioMenuItemConfig("Show current (°C)"): self._show_one,
                RadioMenuItemConfig("Show extra (°C)"): self._show_three,
            }
        )

    def _render(self, msg: SocketMessage[TemperatureInfo]):
        orig_values = msg.data.values_c
        sorted_values = sorted(orig_values, key=lambda v: v[1], reverse=True)

        max_value = 0
        if len(sorted_values) > 0:
            max_value = sorted_values[0][1]

        values_limit = 3 if self._show_three else 1
        top_values_origin_indexes = []
        for (k, v) in sorted_values[:values_limit]:
            top_values_origin_indexes.append(orig_values.index((k, v)))

        values_str = []
        guide = []
        warning = False
        for oindex in sorted(top_values_origin_indexes):
            _, val = orig_values[oindex]
            if val > 90:  # @TODO to config
                warning = True
            val_str = str(round(val)).rjust(2)
            values_str.append(val_str)
            guide.append("1" + val_str[-2:])

        self._render_result(
            self._format_result(*values_str),
            self._format_result(*guide),
            warning,
            icon=self._select_icon(max_value),
        )

    def _format_result(self, *result: str) -> str:
        parts = []
        if self._show_three:
            parts += result[:3]
        elif self._show_one:
            parts += result[:1]
        if len(parts):
            parts += ["°C"]
        return " ".join(parts)
