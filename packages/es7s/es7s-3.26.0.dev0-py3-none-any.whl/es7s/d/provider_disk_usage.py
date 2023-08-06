# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

import psutil

from ._base import DataProvider
from ..shared.dto import DiskUsageInfo


class DiskUsageProvider(DataProvider[DiskUsageInfo]):
    def __init__(self):
        super().__init__('disk', 'disk')

    def _collect(self) -> DiskUsageInfo:
        root_du = psutil.disk_usage('/')
        return DiskUsageInfo(
            free=root_du.free,
            total=root_du.total,
            used_perc=root_du.percent,
        )
