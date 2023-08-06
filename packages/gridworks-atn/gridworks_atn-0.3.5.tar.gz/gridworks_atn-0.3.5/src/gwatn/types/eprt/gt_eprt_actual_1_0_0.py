"""MessageMaker for gt.eprt.actual.1_0_0"""

import datetime
import time
import uuid
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from gridworks.errors import *

from gwatn.types.eprt.gt_eprt_actual_1_0_0_payload import GtEprtActual100
from gwatn.types.hack_utils import log_style_utc_date_w_millis


class Gt_Eprt_Actual_1_0_0:
    mp_alias = "gt.eprt.actual.1_0_0"

    @classmethod
    def create_payload_from_camel_dict(cls, d: dict) -> GtEprtActual100:
        if "MpAlias" not in d.keys():
            d["MpAlias"] = "gt.eprt.actual.1_0_0"
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
        p = GtEprtActual100(
            MpAlias=d["MpAlias"],
            PNodeAlias=d["PNodeAlias"],
            FirstMarketSlotStartIso8601Utc=d["FirstMarketSlotStartIso8601Utc"],
            MethodAlias=d["MethodAlias"],
            TimezoneString=d["TimezoneString"],
            MarketSlotDurationMinutes=d["MarketSlotDurationMinutes"],
            CurrencyUnit=d["CurrencyUnit"],
            Prices=d["Prices"],
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
        p_node_alias: str,
        first_market_slot_start_iso8601_utc: str,
        method_alias: str,
        timezone_string: str,
        market_slot_duration_minutes: int,
        currency_unit: str,
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

        p = GtEprtActual100(
            MpAlias=Gt_Eprt_Actual_1_0_0.mp_alias,
            PNodeAlias=p_node_alias,
            FirstMarketSlotStartIso8601Utc=first_market_slot_start_iso8601_utc,
            MethodAlias=method_alias,
            TimezoneString=timezone_string,
            MarketSlotDurationMinutes=market_slot_duration_minutes,
            CurrencyUnit=currency_unit,
            Prices=prices,
            Comment=comment,
        )

        is_valid, errors = p.is_valid()
        if is_valid is False:
            raise SchemaError(f"Failed to create payload due to these errors: {errors}")
        self.payload = p
