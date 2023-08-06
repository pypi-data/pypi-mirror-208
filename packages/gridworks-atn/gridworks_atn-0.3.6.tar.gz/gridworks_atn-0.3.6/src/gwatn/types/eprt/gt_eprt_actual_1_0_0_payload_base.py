"""PayloadBase for gt.eprt.actual.1_0_0"""
import datetime
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Tuple

import gwatn.types.hack_property_format as property_format


class PayloadBase(NamedTuple):
    PNodeAlias: str  #
    FirstMarketSlotStartIso8601Utc: str  #
    MethodAlias: str  #
    TimezoneString: str  #
    MarketSlotDurationMinutes: int  #
    CurrencyUnit: str  #
    Comment: str  #
    Prices: List[float]
    MpAlias: str = "gt.eprt.actual.1_0_0"

    def asdict(self):
        d = self._asdict()
        return d

    def passes_derived_validations(self) -> Tuple[bool, Optional[List[str]]]:
        is_valid = True
        errors = []
        if self.MpAlias != "gt.eprt.actual.1_0_0":
            is_valid = False
            errors.append(
                f"Payload requires MpAlias of gt.eprt.actual.1_0_0, not {self.MpAlias}."
            )
        if not isinstance(self.PNodeAlias, str):
            is_valid = False
            errors.append(f"PNodeAlias {self.PNodeAlias} must have type str.")
        if not property_format.is_lrd_alias_format(self.PNodeAlias):
            is_valid = False
            errors.append(
                f"PNodeAlias {self.PNodeAlias} must have format GNodeLrdAliasFormat."
            )
        if not isinstance(self.FirstMarketSlotStartIso8601Utc, str):
            is_valid = False
            errors.append(
                f"FirstMarketSlotStartIso8601Utc {self.FirstMarketSlotStartIso8601Utc} must have type str."
            )
        if not property_format.is_recognized_iso8601_utc(
            self.FirstMarketSlotStartIso8601Utc
        ):
            is_valid = False
            errors.append(
                f"FirstMarketSlotStartIso8601Utc {self.FirstMarketSlotStartIso8601Utc} must have format RecognizedIso8601Utc."
            )
        if not isinstance(self.MethodAlias, str):
            is_valid = False
            errors.append(f"MethodAlias {self.MethodAlias} must have type str.")
        if not property_format.is_recognized_price_method(self.MethodAlias):
            is_valid = False
            errors.append(
                f"MethodAlias {self.MethodAlias} must have format RecognizedPriceMethod."
            )
        if not isinstance(self.TimezoneString, str):
            is_valid = False
            errors.append(f"TimezoneString {self.TimezoneString} must have type str.")
        if not property_format.is_recognized_timezone_string(self.TimezoneString):
            is_valid = False
            errors.append(
                f"TimezoneString {self.TimezoneString} must have format RecognizedTimezoneString."
            )
        if not isinstance(self.MarketSlotDurationMinutes, int):
            is_valid = False
            errors.append(
                f"MarketSlotDurationMinutes {self.MarketSlotDurationMinutes} must have type int."
            )
        if not isinstance(self.CurrencyUnit, str):
            is_valid = False
            errors.append(f"CurrencyUnit {self.CurrencyUnit} must have type str.")
        if not property_format.is_recognized_currency_unit(self.CurrencyUnit):
            is_valid = False
            errors.append(
                f"CurrencyUnit {self.CurrencyUnit} must have format RecognizedCurrencyUnit."
            )
        if not isinstance(self.Prices, list):
            is_valid = False
            errors.append(f"Prices {self.Prices} must have type list.")
        else:
            for elt in self.Prices:
                if not isinstance(elt, float):
                    is_valid = False
                    errors.append(
                        f"Elements of the list Prices must have type float. Error with {elt}"
                    )
        if not isinstance(self.Comment, str):
            is_valid = False
            errors.append(f"Comment {self.Comment} must have type str.")
        return is_valid, errors
