"""Payload for r.weather.forecast.1_0_0"""
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from gwatn.types.ws_forecast_gnode.r_weather_forecast.r_weather_forecast_1_0_0_payload_base import (
    PayloadBase,
)


class Payload(PayloadBase):
    def is_valid(self) -> Tuple[bool, Optional[List[str]]]:
        is_valid, errors = self.passes_derived_validations()
        (
            next_is_valid,
            next_errors,
        ) = self.weather100_list_length_consistency_validation()
        is_valid = is_valid and next_is_valid
        errors += next_errors
        (
            next_is_valid,
            next_errors,
        ) = self.weather_forecast100_data_existence_consistency_validation()
        is_valid = is_valid and next_is_valid
        errors += next_errors
        if len(errors) > 0:
            errors.insert(0, "Errors making r.weather.forecast.1_0_0 msg.")
        return is_valid, errors

    # hand-code schema axiom validations below
    def weather100_list_length_consistency_validation(
        self,
    ) -> Tuple[bool, Optional[List[str]]]:
        """WeatherLists = Filter(lambda x: len(x) > 0,  [IrradianceWPerM2, OpaqueCloudCoveragePercents,
                Temperatures]).

        All WeatherLists must have the same length as SliceDurationHrs"""
        return True, []

    def weather_forecast100_data_existence_consistency_validation(
        self,
    ) -> Tuple[bool, Optional[List[str]]]:
        """IrradianceWPerM2 exists iff IrradianceSourceAlias exists iff IrradianceMethodAlias
                exists iff IrradianceType exists

        OpaqueCloudCoveragePercents exists
                iff SkyClaritySourceAlias exists iff SkyClarityMethodAlias exists

        Temperatures
                exist iff TempUnit exists iff TempSourceAlias exists iff TempMethodAlias
                exists"""
        return True, []
