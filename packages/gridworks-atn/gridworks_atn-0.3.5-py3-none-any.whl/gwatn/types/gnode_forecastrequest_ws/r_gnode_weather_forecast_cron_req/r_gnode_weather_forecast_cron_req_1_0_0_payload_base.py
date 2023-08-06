"""PayloadBase for r.gnode.weather.forecast.cron.req.1_0_0"""
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
    ToGNodeAlias: str  #
    MessageId: str  #
    SendHour: str  #
    IncludeSkyClarity: bool  #
    IncludeIrradiance: bool  #
    IncludeTemp: bool  #
    FirstValueOffsetSeconds: int  #
    TimezoneString: str  #
    SendMinute: int  #
    SendSecond: int  #
    LocationAlias: str  #
    RepeatBroadcastDelaySeconds: List[int]
    SliceDurationMinutes: List[int]
    IrradianceMethodAlias: Optional[str] = None
    IrradianceSourceAlias: Optional[str] = None
    TempMethodAlias: Optional[str] = None
    SkyClarityMethodAlias: Optional[str] = None
    TempSourceAlias: Optional[str] = None
    IrlTimeUtc: Optional[str] = None
    SkyClaritySourceAlias: Optional[str] = None
    TempUnit: Optional[str] = None
    IrradianceType: Optional[str] = None
    WorldInstanceAlias: Optional[str] = None
    MpAlias: str = "r.gnode.weather.forecast.cron.req.1_0_0"

    def asdict(self):
        d = self._asdict()
        if d["WorldInstanceAlias"] is None:
            del d["WorldInstanceAlias"]
        if d["IrradianceMethodAlias"] is None:
            del d["IrradianceMethodAlias"]
        if d["IrradianceSourceAlias"] is None:
            del d["IrradianceSourceAlias"]
        if d["TempMethodAlias"] is None:
            del d["TempMethodAlias"]
        if d["SkyClarityMethodAlias"] is None:
            del d["SkyClarityMethodAlias"]
        if d["TempSourceAlias"] is None:
            del d["TempSourceAlias"]
        if d["IrlTimeUtc"] is None:
            del d["IrlTimeUtc"]
        if d["SkyClaritySourceAlias"] is None:
            del d["SkyClaritySourceAlias"]
        if d["TempUnit"] is None:
            del d["TempUnit"]
        if d["IrradianceType"] is None:
            del d["IrradianceType"]
        return d

    def passes_derived_validations(self) -> Tuple[bool, Optional[List[str]]]:
        is_valid = True
        errors = []
        if self.MpAlias != "r.gnode.weather.forecast.cron.req.1_0_0":
            is_valid = False
            errors.append(
                f"Payload requires MpAlias of r.gnode.weather.forecast.cron.req.1_0_0, not {self.MpAlias}."
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
        if not isinstance(self.ToGNodeAlias, str):
            is_valid = False
            errors.append(f"ToGNodeAlias {self.ToGNodeAlias} must have type str.")
        if not property_format.is_lrd_alias_format(self.ToGNodeAlias):
            is_valid = False
            errors.append(
                f"ToGNodeAlias {self.ToGNodeAlias} must have format GNodeLrdAliasFormat."
            )
        if not isinstance(self.MessageId, str):
            is_valid = False
            errors.append(f"MessageId {self.MessageId} must have type str.")
        if not property_format.is_uuid_canonical_textual(self.MessageId):
            is_valid = False
            errors.append(
                f"MessageId {self.MessageId} must have format UuidCanonicalTextual."
            )
        if not isinstance(self.SendHour, str):
            is_valid = False
            errors.append(f"SendHour {self.SendHour} must have type str.")
        if not property_format.is_simple_cron24(self.SendHour):
            is_valid = False
            errors.append(f"SendHour {self.SendHour} must have format SimpleCron24.")
        if not isinstance(self.IncludeSkyClarity, bool):
            is_valid = False
            errors.append(
                f"IncludeSkyClarity {self.IncludeSkyClarity} must have type bool."
            )
        if not isinstance(self.IncludeIrradiance, bool):
            is_valid = False
            errors.append(
                f"IncludeIrradiance {self.IncludeIrradiance} must have type bool."
            )
        if not isinstance(self.IncludeTemp, bool):
            is_valid = False
            errors.append(f"IncludeTemp {self.IncludeTemp} must have type bool.")
        if not isinstance(self.FirstValueOffsetSeconds, int):
            is_valid = False
            errors.append(
                f"FirstValueOffsetSeconds {self.FirstValueOffsetSeconds} must have type int."
            )
        if not isinstance(self.TimezoneString, str):
            is_valid = False
            errors.append(f"TimezoneString {self.TimezoneString} must have type str.")
        if not property_format.is_recognized_timezone_string(self.TimezoneString):
            is_valid = False
            errors.append(
                f"TimezoneString {self.TimezoneString} must have format RecognizedTimezoneString."
            )
        if not isinstance(self.SendMinute, int):
            is_valid = False
            errors.append(f"SendMinute {self.SendMinute} must have type int.")
        if not property_format.is_simple60(self.SendMinute):
            is_valid = False
            errors.append(f"SendMinute {self.SendMinute} must have format Simple60.")
        if not isinstance(self.SendSecond, int):
            is_valid = False
            errors.append(f"SendSecond {self.SendSecond} must have type int.")
        if not property_format.is_simple60(self.SendSecond):
            is_valid = False
            errors.append(f"SendSecond {self.SendSecond} must have format Simple60.")
        if not isinstance(self.LocationAlias, str):
            is_valid = False
            errors.append(f"LocationAlias {self.LocationAlias} must have type str.")
        if not isinstance(self.RepeatBroadcastDelaySeconds, list):
            is_valid = False
            errors.append(
                f"RepeatBroadcastDelaySeconds {self.RepeatBroadcastDelaySeconds} must have type list."
            )
        else:
            for elt in self.RepeatBroadcastDelaySeconds:
                if not isinstance(elt, int):
                    is_valid = False
                    errors.append(
                        f"Elements of the list RepeatBroadcastDelaySeconds must have type int. Error with {elt}"
                    )
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
        if self.IrradianceMethodAlias:
            if not isinstance(self.IrradianceMethodAlias, str):
                is_valid = False
                errors.append(
                    f"IrradianceMethodAlias {self.IrradianceMethodAlias} must have type str."
                )
            if not property_format.is_weather_method(self.IrradianceMethodAlias):
                is_valid = False
                errors.append(
                    f"IrradianceMethodAlias {self.IrradianceMethodAlias} must have format WeatherMethod."
                )
        if self.IrradianceSourceAlias:
            if not isinstance(self.IrradianceSourceAlias, str):
                is_valid = False
                errors.append(
                    f"IrradianceSourceAlias {self.IrradianceSourceAlias} must have type str."
                )
            if not property_format.is_weather_source(self.IrradianceSourceAlias):
                is_valid = False
                errors.append(
                    f"IrradianceSourceAlias {self.IrradianceSourceAlias} must have format WeatherSource."
                )
        if self.TempMethodAlias:
            if not isinstance(self.TempMethodAlias, str):
                is_valid = False
                errors.append(
                    f"TempMethodAlias {self.TempMethodAlias} must have type str."
                )
            if not property_format.is_weather_method(self.TempMethodAlias):
                is_valid = False
                errors.append(
                    f"TempMethodAlias {self.TempMethodAlias} must have format WeatherMethod."
                )
        if self.SkyClarityMethodAlias:
            if not isinstance(self.SkyClarityMethodAlias, str):
                is_valid = False
                errors.append(
                    f"SkyClarityMethodAlias {self.SkyClarityMethodAlias} must have type str."
                )
            if not property_format.is_weather_method(self.SkyClarityMethodAlias):
                is_valid = False
                errors.append(
                    f"SkyClarityMethodAlias {self.SkyClarityMethodAlias} must have format WeatherMethod."
                )
        if self.TempSourceAlias:
            if not isinstance(self.TempSourceAlias, str):
                is_valid = False
                errors.append(
                    f"TempSourceAlias {self.TempSourceAlias} must have type str."
                )
            if not property_format.is_weather_source(self.TempSourceAlias):
                is_valid = False
                errors.append(
                    f"TempSourceAlias {self.TempSourceAlias} must have format WeatherSource."
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
        if self.SkyClaritySourceAlias:
            if not isinstance(self.SkyClaritySourceAlias, str):
                is_valid = False
                errors.append(
                    f"SkyClaritySourceAlias {self.SkyClaritySourceAlias} must have type str."
                )
            if not property_format.is_weather_source(self.SkyClaritySourceAlias):
                is_valid = False
                errors.append(
                    f"SkyClaritySourceAlias {self.SkyClaritySourceAlias} must have format WeatherSource."
                )
        if self.TempUnit:
            if not isinstance(self.TempUnit, str):
                is_valid = False
                errors.append(f"TempUnit {self.TempUnit} must have type str.")
            if not property_format.is_recognized_temperature_unit(self.TempUnit):
                is_valid = False
                errors.append(
                    f"TempUnit {self.TempUnit} must have format RecognizedTemperatureUnit."
                )
        if self.IrradianceType:
            if not isinstance(self.IrradianceType, str):
                is_valid = False
                errors.append(
                    f"IrradianceType {self.IrradianceType} must have type str."
                )
            if not property_format.is_recognized_irradiance_type(self.IrradianceType):
                is_valid = False
                errors.append(
                    f"IrradianceType {self.IrradianceType} must have format RecognizedIrradianceType."
                )
        return is_valid, errors
