"""PayloadBase for r.distp.1_0_0"""
import datetime
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Tuple

import gwatn.types.hack_property_format as property_format


class PayloadBase(NamedTuple):
    FromGNodeAlias: str  #
    FromGNodeInstanceId: str  #
    MessageId: str  #
    StartYearUtc: int  #
    PriceUid: str  #
    CurrencyUnit: str  #
    MethodAlias: str  #
    StartMinuteUtc: int  #
    StartDayUtc: int  #
    PNodeAlias: str  #
    StartHourUtc: int  #
    StartMonthUtc: int  #
    Comment: str  #
    TimezoneString: str  #
    Prices: List[float]
    SliceDurationMinutes: List[int]
    IrlTimeUtc: Optional[str] = None
    WorldInstanceAlias: Optional[str] = None
    MpAlias: str = "r.distp.1_0_0"

    def asdict(self):
        d = self._asdict()
        if d["WorldInstanceAlias"] is None:
            del d["WorldInstanceAlias"]
        if d["IrlTimeUtc"] is None:
            del d["IrlTimeUtc"]
        return d

    def passes_derived_validations(self) -> Tuple[bool, Optional[List[str]]]:
        is_valid = True
        errors = []
        if self.MpAlias != "r.distp.1_0_0":
            is_valid = False
            errors.append(
                f"Payload requires MpAlias of r.distp.1_0_0, not {self.MpAlias}."
            )
        if not isinstance(self.FromGNodeAlias, str):
            is_valid = False
            errors.append(f"FromGNodeAlias {self.FromGNodeAlias} must have type str.")
        if not property_format.is_lrd_alias_format(self.FromGNodeAlias):
            is_valid = False
            errors.append(
                f"FromGNodeAlias {self.FromGNodeAlias} must have format GNodeLrdAliasFormat."
            )
        if not isinstance(self.FromGNodeInstanceId, str):
            is_valid = False
            errors.append(
                f"FromGNodeInstanceId {self.FromGNodeInstanceId} must have type str."
            )
        if not property_format.is_uuid_canonical_textual(self.FromGNodeInstanceId):
            is_valid = False
            errors.append(
                f"FromGNodeInstanceId {self.FromGNodeInstanceId} must have format UuidCanonicalTextual."
            )
        if not isinstance(self.MessageId, str):
            is_valid = False
            errors.append(f"MessageId {self.MessageId} must have type str.")
        if not property_format.is_uuid_canonical_textual(self.MessageId):
            is_valid = False
            errors.append(
                f"MessageId {self.MessageId} must have format UuidCanonicalTextual."
            )
        if not isinstance(self.StartYearUtc, int):
            is_valid = False
            errors.append(f"StartYearUtc {self.StartYearUtc} must have type int.")
        try:
            datetime.datetime(
                year=self.StartYearUtc,
                month=self.StartMonthUtc,
                day=self.StartDayUtc,
                hour=self.StartHourUtc,
            )
        except ValueError as e:
            is_valid = False
            errors.append(e)
        if not isinstance(self.PriceUid, str):
            is_valid = False
            errors.append(f"PriceUid {self.PriceUid} must have type str.")
        if not property_format.is_uuid_canonical_textual(self.PriceUid):
            is_valid = False
            errors.append(
                f"PriceUid {self.PriceUid} must have format UuidCanonicalTextual."
            )
        if not isinstance(self.CurrencyUnit, str):
            is_valid = False
            errors.append(f"CurrencyUnit {self.CurrencyUnit} must have type str.")
        if not property_format.is_recognized_currency_unit(self.CurrencyUnit):
            is_valid = False
            errors.append(
                f"CurrencyUnit {self.CurrencyUnit} must have format RecognizedCurrencyUnit."
            )
        if not isinstance(self.MethodAlias, str):
            is_valid = False
            errors.append(f"MethodAlias {self.MethodAlias} must have type str.")
        if not property_format.is_recognized_price_method(self.MethodAlias):
            is_valid = False
            errors.append(
                f"MethodAlias {self.MethodAlias} must have format RecognizedPriceMethod."
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
        if not isinstance(self.StartMinuteUtc, int):
            is_valid = False
            errors.append(f"StartMinuteUtc {self.StartMinuteUtc} must have type int.")
        if not 0 <= self.StartMinuteUtc <= 60:
            is_valid = False
            errors.append("StartMinuteUtc must be in 0..59")
        if not isinstance(self.StartDayUtc, int):
            is_valid = False
            errors.append(f"StartDayUtc {self.StartDayUtc} must have type int.")
        if not isinstance(self.PNodeAlias, str):
            is_valid = False
            errors.append(f"PNodeAlias {self.PNodeAlias} must have type str.")
        if not property_format.is_lrd_alias_format(self.PNodeAlias):
            is_valid = False
            errors.append(
                f"PNodeAlias {self.PNodeAlias} must have format GNodeLrdAliasFormat."
            )
        if not isinstance(self.StartHourUtc, int):
            is_valid = False
            errors.append(f"StartHourUtc {self.StartHourUtc} must have type int.")
        if not isinstance(self.StartMonthUtc, int):
            is_valid = False
            errors.append(f"StartMonthUtc {self.StartMonthUtc} must have type int.")
        if not isinstance(self.Comment, str):
            is_valid = False
            errors.append(f"Comment {self.Comment} must have type str.")
        if not isinstance(self.SliceDurationMinutes, list):
            is_valid = False
            errors.append(
                f"SliceDurationMinutes {self.SliceDurationMinutes} must have type list."
            )
        else:
            for elt in self.SliceDurationMinutes:
                if not isinstance(elt, int):
                    is_valid = False
                    errors.append(
                        f"Elements of the list SliceDurationMinutes must have type int. Error with {elt}"
                    )
        if not isinstance(self.TimezoneString, str):
            is_valid = False
            errors.append(f"TimezoneString {self.TimezoneString} must have type str.")
        if not property_format.is_recognized_timezone_string(self.TimezoneString):
            is_valid = False
            errors.append(
                f"TimezoneString {self.TimezoneString} must have format RecognizedTimezoneString."
            )
        if self.WorldInstanceAlias:
            if not isinstance(self.WorldInstanceAlias, str):
                is_valid = False
                errors.append(
                    f"WorldInstanceAlias {self.WorldInstanceAlias} must have type str."
                )
            if not property_format.is_world_instance_alias_format(
                self.WorldInstanceAlias
            ):
                is_valid = False
                errors.append(
                    f"WorldInstanceAlias {self.WorldInstanceAlias} must have format WorldInstanceAliasFormat"
                )
        if self.IrlTimeUtc:
            if not isinstance(self.IrlTimeUtc, str):
                is_valid = False
                errors.append(f"IrlTimeUtc {self.IrlTimeUtc} must have type str.")
            if not property_format.is_log_style_utc_date_w_millis(self.IrlTimeUtc):
                is_valid = False
                errors.append(
                    f"IrlTimeUtc {self.IrlTimeUtc} must have format LogStyleUtcDateWMillis."
                )
        return is_valid, errors
