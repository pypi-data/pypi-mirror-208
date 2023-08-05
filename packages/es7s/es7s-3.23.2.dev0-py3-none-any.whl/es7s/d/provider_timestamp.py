# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import re


from ._base import DataProvider
from ..shared import get_config
from ..shared.dto import TimestampInfo


class TimestampProvider(DataProvider[TimestampInfo]):
    def __init__(self):
        super().__init__("timestamp", "timestamp", 23.0)

    def _collect(self) -> TimestampInfo:
        url = get_config().get('provider.'+self._config_var, 'url')
        response = self._make_request(url)
        data = response.text
        if data_match := re.match(r'(\d{10})', data.strip()):
            data = int(data_match.group(1))
            return TimestampInfo(ts=data)
        return TimestampInfo()
