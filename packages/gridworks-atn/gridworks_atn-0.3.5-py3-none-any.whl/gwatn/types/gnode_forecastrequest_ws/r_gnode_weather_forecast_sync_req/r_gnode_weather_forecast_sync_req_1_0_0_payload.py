"""Payload for r.gnode.weather.forecast.sync.req.1_0_0"""
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from gwatn.types.gnode_forecastrequest_ws.r_gnode_weather_forecast_sync_req.r_gnode_weather_forecast_sync_req_1_0_0_payload_base import (
    PayloadBase,
)


class Payload(PayloadBase):
    def is_valid(self) -> Tuple[bool, Optional[List[str]]]:
        is_valid, errors = self.passes_derived_validations()
        (
            next_is_valid,
            next_errors,
        ) = self.forecast_weather_request_data_existence_consistency100_validation()
        is_valid = is_valid and next_is_valid
        errors += next_errors
        if len(errors) > 0:
            errors.insert(
                0, "Errors making r.gnode.weather.forecast.sync.req.1_0_0 msg."
            )
        return is_valid, errors

    # hand-code schema axiom validations below
    def forecast_weather_request_data_existence_consistency100_validation(
        self,
    ) -> Tuple[bool, Optional[List[str]]]:
        """If IncludeTemp is True, then TempSourceAlias and TempMethodAlias and TempUnit
                must exist.
        If IncludeSkyClarity is True, then SkyClaritySourceAlias and
                SkyClarityMethodAlias must exist.
        If IncludeIrradiance is True, then IrradianceSourceAlias
                and IrradianceMethodAlias and IrradianceType must exist."""
        return True, []
