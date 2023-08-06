"""MessageMaker for gt.epda.actual.1_0_0"""

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from gridworks.errors import *

from gwatn.types.epda.gt_epda_actual_1_0_0_payload import GtEpdaActual100


class Gt_Epda_Actual_1_0_0:
    mp_alias = "gt.epda.actual.1_0_0"

    @classmethod
    def create_payload_from_camel_dict(cls, d: dict) -> GtEpdaActual100:
        if "MpAlias" not in d.keys():
            d["MpAlias"] = "gt.epda.actual.1_0_0"
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
        p = GtEpdaActual100(
            MpAlias=d["MpAlias"],
            TimezoneString=d["TimezoneString"],
            Comment=d["Comment"],
            PNodeAlias=d["PNodeAlias"],
            CurrencyUnit=d["CurrencyUnit"],
            FirstMarketSlotStartIso8601Utc=d["FirstMarketSlotStartIso8601Utc"],
            MarketSlotDurationMinutes=d["MarketSlotDurationMinutes"],
            Prices=d["Prices"],
            MethodAlias=d["MethodAlias"],
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
        timezone_string: str,
        comment: str,
        p_node_alias: str,
        currency_unit: str,
        first_market_slot_start_iso8601_utc: str,
        market_slot_duration_minutes: int,
        method_alias: str,
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

        p = GtEpdaActual100(
            MpAlias=Gt_Epda_Actual_1_0_0.mp_alias,
            TimezoneString=timezone_string,
            Comment=comment,
            PNodeAlias=p_node_alias,
            CurrencyUnit=currency_unit,
            FirstMarketSlotStartIso8601Utc=first_market_slot_start_iso8601_utc,
            MarketSlotDurationMinutes=market_slot_duration_minutes,
            Prices=prices,
            MethodAlias=method_alias,
        )

        is_valid, errors = p.is_valid()
        if is_valid is False:
            raise SchemaError(f"Failed to create payload due to these errors: {errors}")
        self.payload = p
