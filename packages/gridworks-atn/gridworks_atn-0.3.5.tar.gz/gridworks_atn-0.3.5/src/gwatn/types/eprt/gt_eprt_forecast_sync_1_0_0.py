"""MessageMaker for gt.eprt.forecast.sync.1_0_0"""

import datetime
import time
import uuid
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from gridworks.errors import *

from gwatn.types.eprt.gt_eprt_forecast_sync_1_0_0_payload import GtEprtForecastSync100
from gwatn.types.hack_utils import log_style_utc_date_w_millis


class Gt_Eprt_Forecast_Sync_1_0_0:
    mp_alias = "gt.eprt.forecast.sync.1_0_0"

    @classmethod
    def create_payload_from_camel_dict(cls, d: dict) -> GtEprtForecastSync100:
        if "MpAlias" not in d.keys():
            d["MpAlias"] = "gt.eprt.forecast.sync.1_0_0"
        list_as_floats = []
        if not isinstance(d["Prices"], list):
            raise SchemaError('d["Prices"] must be a list!!')
        for elt in d["Prices"]:
            try:
                list_as_floats.append(float(elt))
            except ValueError:
                pass  # This will get caught in is_valid() check below
        d["Prices"] = list_as_floats
        if "WorldInstanceAlias" not in d.keys():
            d["WorldInstanceAlias"] = None
        p = GtEprtForecastSync100(
            MpAlias=d["MpAlias"],
            MethodAlias=d["MethodAlias"],
            Prices=d["Prices"],
            PNodeAlias=d["PNodeAlias"],
            TimezoneString=d["TimezoneString"],
            CurrencyUnit=d["CurrencyUnit"],
            UniformSliceDurationMinutes=d["UniformSliceDurationMinutes"],
            ForecastStartIso8601Utc=d["ForecastStartIso8601Utc"],
            ForecastGeneratedIso8601Utc=d["ForecastGeneratedIso8601Utc"],
            PriceUid=d["PriceUid"],
            Comment=d["Comment"],
        )
        is_valid, errors = p.is_valid()
        if not is_valid:
            raise SchemaError(errors)
        return p

    @classmethod
    def payload_is_valid(
        cls, payload_as_dict: Dict[str, Any]
    ) -> Tuple[bool, Optional[List[str]]]:
        try:
            p = cls.create_payload_from_camel_dict(payload_as_dict)
        except SchemaError as e:
            errors = [e]
            return False, errors
        return p.is_valid()

    def __init__(
        self,
        method_alias: str,
        p_node_alias: str,
        timezone_string: str,
        currency_unit: str,
        uniform_slice_duration_minutes: int,
        forecast_start_iso8601_utc: str,
        forecast_generated_iso8601_utc: str,
        price_uid: str,
        comment: str,
        prices: List[float],
    ):
        self.errors = []
        self.payload = None
        if not isinstance(prices, list):
            raise SchemaError(f"prices must be a list!!")
        try:
            tmp_prices = []
            for elt in prices:
                tmp_prices.append(float(elt))
            prices = tmp_prices
        except ValueError:
            pass  # This will get caught in is_valid() check below

        p = GtEprtForecastSync100(
            MpAlias=Gt_Eprt_Forecast_Sync_1_0_0.mp_alias,
            MethodAlias=method_alias,
            Prices=prices,
            PNodeAlias=p_node_alias,
            TimezoneString=timezone_string,
            CurrencyUnit=currency_unit,
            UniformSliceDurationMinutes=uniform_slice_duration_minutes,
            ForecastStartIso8601Utc=forecast_start_iso8601_utc,
            ForecastGeneratedIso8601Utc=forecast_generated_iso8601_utc,
            PriceUid=price_uid,
            Comment=comment,
        )

        is_valid, errors = p.is_valid()
        if is_valid is False:
            raise SchemaError(f"Failed to create payload due to these errors: {errors}")
        self.payload = p
