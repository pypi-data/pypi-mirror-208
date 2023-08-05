# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import pytermor as pt

from .log import get_logger
from .config import get_config


REGULAR_TO_BRIGHT_COLOR_MAP = {
    pt.cv.BLACK: pt.cv.GRAY,
    pt.cv.RED: pt.cv.HI_RED,
    pt.cv.GREEN: pt.cv.HI_GREEN,
    pt.cv.YELLOW: pt.cv.HI_YELLOW,
    pt.cv.BLUE: pt.cv.HI_BLUE,
    pt.cv.MAGENTA: pt.cv.HI_MAGENTA,
    pt.cv.CYAN: pt.cv.HI_CYAN,
    pt.cv.WHITE: pt.cv.HI_WHITE,
}


# noinspection PyMethodMayBeStatic
class Color:
    def get_color_name(self) -> str:
        return get_config().get("general", "theme-color", fallback="red")

    def get_theme_color(self, strict: bool = False, ctype: type = None) -> pt.IColor:
        try:
            result = pt.resolve_color(self.get_color_name(), ctype)
            if ctype and type(result) != ctype:
                raise TypeError
            return result
        except (LookupError, TypeError):
            if strict:
                raise
            return pt.cv.RED

    def get_theme_bright_color(self) -> pt.CT:
        logger = get_logger()

        def resolve_with_map(origin: pt.Color16) -> pt.IColor:
            result = REGULAR_TO_BRIGHT_COLOR_MAP.get(origin)
            logger.debug(f"Resolved bright color using preset map: {result}")
            return result

        def resolve_by_shift(origin: pt.IColor) -> pt.IColor:
            origin_hsv = origin.to_hsv()
            hue, sat, val = origin_hsv
            val += 0.40
            if val > 1.0:
                # brightness increase by saturation decrease when value is max
                sat = max(0, sat - (val - 1.0) / 2)
                val = 1.0

            result_hsv = pt.common.HSV(hue, sat, val)
            msg = f"Resolving bright color via S/V channel shift: {origin_hsv} -> {result_hsv}"
            get_logger().debug(msg)
            return pt.ColorRGB(hex_value=pt.hsv_to_hex(result_hsv))

        try:
            theme_color16 = pt.resolve_color(self.get_color_name(), pt.Color16)
            logger.debug(f"Theme color is valid Color16: {theme_color16}")
            if theme_color16 in REGULAR_TO_BRIGHT_COLOR_MAP.keys():
                return resolve_with_map(theme_color16)
        except LookupError:
            pass

        theme_color = self.get_theme_color()
        if isinstance(theme_color, pt.Color256):
            logger.debug(f"Theme color is valid Color256: {theme_color}")
            if theme_color16 := theme_color._color16_equiv:
                if theme_color16 in REGULAR_TO_BRIGHT_COLOR_MAP.keys():
                    return resolve_with_map(theme_color16)

        logger.debug(f"No mapped bright color: {theme_color}")
        return resolve_by_shift(theme_color)

    def get_monitor_separator_color(self) -> pt.CT:
        hue, _, _ = self.get_theme_color().to_hsv()
        return pt.ColorRGB(hex_value=pt.hsv_to_hex(hue, 0.59, 0.50))


_color = Color()


def get_color() -> Color:
    return _color
