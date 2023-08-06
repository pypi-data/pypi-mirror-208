"""Payload for r.weather.forecast.raw.1_0_0"""
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from gwatn.types.ws_forecast_gnode.r_weather_forecast_raw.r_weather_forecast_raw_1_0_0_payload_base import (
    PayloadBase,
)


class Payload(PayloadBase):
    def is_valid(self) -> Tuple[bool, Optional[List[str]]]:
        is_valid, errors = self.passes_derived_validations()
        if len(errors) > 0:
            errors.insert(0, "Errors making r.weather.forecast.raw.1_0_0 msg.")
        return is_valid, errors

    # hand-code schema axiom validations below
    # TODO: make sure elts of lists Temperatures, OpaqueCloudCoveragePercents and IrradianceWPerM2 are
    # all either ints or 'X'
    # Also figure out why the code derivation did not check that they were ints!
