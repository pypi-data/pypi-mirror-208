from datetime import datetime

from uplink import Consumer, Query, get, response_handler, returns

from bpkio_api.models.Consumption import ConsumptionData
from bpkio_api.response_handler import raise_for_status


@response_handler(raise_for_status)
class ConsumptionApi(Consumer):
    def __init__(self, base_url="", **kwargs):
        super().__init__(base_url, **kwargs)

    @returns.json()
    @get("consumption")
    def retrieve(
        self,
        start_time: Query("start-time"),  # type: ignore
        end_time: Query("end-time"),  # type: ignore
    ) -> ConsumptionData:  # type: ignore
        """Get the consumption data between 2 dates"""
