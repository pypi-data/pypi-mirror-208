# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

import pytermor as pt
from pytermor import Style, CDT, IColor


class FrozenStyle(pt.Style):
    def __init__(
        self,
        fallback: Style = None,
        fg: CDT | IColor = None,
        bg: CDT | IColor = None,
        *,
        bold: bool = None,
        dim: bool = None,
        italic: bool = None,
        underlined: bool = None,
        overlined: bool = None,
        crosslined: bool = None,
        double_underlined: bool = None,
        inversed: bool = None,
        blink: bool = None,
        class_name: str = None
    ):
        super().__init__(
            fallback,
            fg,
            bg,
            frozen=True,
            bold=bold,
            dim=dim,
            italic=italic,
            underlined=underlined,
            overlined=overlined,
            crosslined=crosslined,
            double_underlined=double_underlined,
            inversed=inversed,
            blink=blink,
            class_name=class_name,
        )


class Styles(pt.Styles):
    TEXT_DISABLED = FrozenStyle(fg=pt.cv.GRAY_23)
    TEXT_LABEL = FrozenStyle(fg=pt.cv.GRAY_35)
    TEXT_DEFAULT = FrozenStyle(fg=pt.cv.GRAY_62)

    STATUSBAR_BG = pt.NOOP_COLOR

    VALUE_LBL_5 = TEXT_LABEL
    VALUE_UNIT_4 = TEXT_LABEL
    VALUE_FRAC_3 = FrozenStyle(fg=pt.cv.GRAY_50)
    VALUE_PRIM_2 = TEXT_DEFAULT
    VALUE_PRIM_1 = FrozenStyle(fg=pt.cv.GRAY_70, bold=True)

    TEXT_ACCENT = FrozenStyle(fg=pt.cv.GRAY_85)
    TEXT_SUBTITLE = FrozenStyle(fg=pt.cv.GRAY_93, bold=True)
    TEXT_TITLE = FrozenStyle(fg=pt.cv.HI_WHITE, bold=True, underlined=True)
    TEXT_UPDATED = FrozenStyle(fg=pt.cv.HI_GREEN, bold=True)

    BORDER_DEFAULT = FrozenStyle(fg=pt.cv.GRAY_30)
    FILL_DEFAULT = FrozenStyle(fg=pt.cv.GRAY_46)

    STDERR_DEBUG = FrozenStyle(fg=pt.resolve_color("medium purple 7"))
    STDERR_TRACE = FrozenStyle(fg=pt.resolve_color("pale turquoise 4"))

    # PBAR_BG = pt.Style(bg=pt.cv.GRAY_3)
    PBAR_DEFAULT = FrozenStyle(TEXT_DEFAULT, bg=pt.cv.GRAY_19)
    PBAR_ALERT_1 = FrozenStyle(fg=pt.cv.GRAY_7, bg=pt.resolve_color("orange 3"))
    PBAR_ALERT_2 = FrozenStyle(PBAR_ALERT_1, bg=pt.resolve_color("dark goldenrod"))
    PBAR_ALERT_3 = FrozenStyle(PBAR_ALERT_1, bg=pt.resolve_color("orange 2"))
    PBAR_ALERT_4 = FrozenStyle(PBAR_ALERT_1, bg=pt.resolve_color("dark orange"))
    PBAR_ALERT_5 = FrozenStyle(PBAR_ALERT_1, bg=pt.resolve_color("orange-red 1"))
    PBAR_ALERT_6 = FrozenStyle(PBAR_ALERT_1, bg=pt.resolve_color("red 3"))
    PBAR_ALERT_7 = pt.Styles.CRITICAL_ACCENT

    DEBUG = pt.Style(
        fg=0x8163A2, bg=0x444, underlined=True, overlined=True, blink=False, frozen=True
    )
    DEBUG_SEP_INT = FrozenStyle(fg=0x7280E2)
    DEBUG_SEP_EXT = FrozenStyle(fg=0x7E59A9)
