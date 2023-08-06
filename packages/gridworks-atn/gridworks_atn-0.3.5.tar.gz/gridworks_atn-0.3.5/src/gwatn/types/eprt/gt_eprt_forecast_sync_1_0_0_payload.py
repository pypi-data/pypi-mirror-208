"""Payload for gt.eprt.forecast.sync.1_0_0"""
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import pendulum

from gwatn.types.eprt.gt_eprt_forecast_sync_1_0_0_payload_base import PayloadBase


class GtEprtForecastSync100(PayloadBase):
    def is_valid(self) -> Tuple[bool, Optional[List[str]]]:
        is_valid, errors = self.passes_derived_validations()
        is_valid_inc, errors_inc = self.starts_at_top_of_5_min()
        is_valid = is_valid and is_valid_inc
        errors += errors_inc
        is_valid_inc, errors_inc = self.generate_forecast_before_start()
        is_valid = is_valid and is_valid_inc
        errors += errors_inc
        if len(errors) > 0:
            errors.insert(0, "Errors making gt.eprt.forecast.sync.1_0_0 msg.")
        return is_valid, errors

    # hand-code schema axiom validations below
    def starts_at_top_of_5_min(self):
        is_valid = True
        errors = []
        if pendulum.parse(self.ForecastStartIso8601Utc).int_timestamp % 300 != 0:
            is_valid = False
            errors = [
                f"Forecast start mod 300 is {pendulum.parse(self.ForecastStartIso8601Utc).int_timestamp % 300}. Must be 0"
            ]

        return is_valid, errors

    def generate_forecast_before_start(self):
        if pendulum.parse(self.ForecastGeneratedIso8601Utc) < pendulum.parse(
            self.ForecastStartIso8601Utc
        ):
            return True, []
        else:
            return False, [
                f"Forecast must be generated before start! Forecast generated {self.ForecastGeneratedIso8601Utc} and start is {self.ForecastStartIso8601Utc}"
            ]
