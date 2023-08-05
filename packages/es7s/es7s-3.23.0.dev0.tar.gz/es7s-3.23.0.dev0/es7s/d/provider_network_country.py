# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

from ._base import DataProvider, DataCollectionError
from ..shared.dto import NetworkCountryInfo


class NetworkCountryProvider(DataProvider[NetworkCountryInfo]):
    def __init__(self):
        super().__init__("network-country", "network-country", 17.0)

    def _reset(self):
        return NetworkCountryInfo()

    def _collect(self) -> NetworkCountryInfo:
        fields = [
            "status",
            "message",
            "country",
            "countryCode",
            "mobile",
            "proxy",
            "hosting",
            "query",
        ]
        url = "http://ip-api.com/json?fields=" + ",".join(fields)
        response = self._make_request(url)
        data = response.json()
        if data.get("status") != "success":
            raise DataCollectionError(f"Resolver service error: {data.get('message')}")

        fields = [data.get(k) for k in ["countryCode", "query", "mobile", "proxy", "hosting"]]
        return NetworkCountryInfo(*fields)
