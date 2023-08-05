# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

import psutil

from ._base import DataProvider
from ..shared.dto import MemoryInfo


class MemoryProvider(DataProvider[MemoryInfo]):
    def __init__(self):
        super().__init__('memory', 'memory')

    def _collect(self) -> MemoryInfo:
        return MemoryInfo(
            virtual_used=psutil.virtual_memory().used,
            virtual_total=psutil.virtual_memory().total,
            swap_used=psutil.swap_memory().used,
            swap_total=psutil.swap_memory().total,
        )
