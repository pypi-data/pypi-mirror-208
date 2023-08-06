"""Payload for r.weather.forecast.sync.1_0_0"""
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from gwatn.types.ws_forecast_gnode.r_weather_forecast_sync.r_weather_forecast_sync_1_0_0_payload_base import (
    PayloadBase,
)


class Payload(PayloadBase):
    def is_valid(self) -> Tuple[bool, Optional[List[str]]]:
        is_valid, errors = self.passes_derived_validations()
        (
            next_is_valid,
            next_errors,
        ) = self.weather_sync100_list_length_consistency_validation()
        is_valid = is_valid and next_is_valid
        errors += next_errors
        if len(errors) > 0:
            errors.insert(0, "Errors making r.weather.forecast.sync.1_0_0 msg.")
        return is_valid, errors

    # hand-code schema axiom validations below
    def weather_sync100_list_length_consistency_validation(
        self,
    ) -> Tuple[bool, Optional[List[str]]]:
        """WeatherLists = Filter(lambda x: len(x) > 0,  [IrradianceWPerM2, OpaqueCloudCoveragePercents,
        Temperatures]).

        All WeatherLists must have the same length."""
        return True, []
