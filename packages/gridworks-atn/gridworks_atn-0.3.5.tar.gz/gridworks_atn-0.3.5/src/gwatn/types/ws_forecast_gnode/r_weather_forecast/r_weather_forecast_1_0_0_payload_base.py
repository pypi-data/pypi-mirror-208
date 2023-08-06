"""PayloadBase for r.weather.forecast.1_0_0"""
import datetime
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Tuple

import gwatn.types.hack_property_format as property_format


class PayloadBase(NamedTuple):
    FromGNodeInstanceId: str  #
    MessageId: str  #
    FromGNodeAlias: str  #
    StartYearUtc: int  #
    WeatherUid: str  #
    StartMonthUtc: int  #
    StartDayUtc: int  #
    StartHourUtc: int  #
    ForecastUnixTimeS: int  #
    StartMinuteUtc: int  #
    Comment: str  #
    TimezoneString: str  #
    LocationAlias: str  #
    SliceDurationMinutes: List[int]
    SkyClarityMethodAlias: Optional[str] = None
    IrradianceType: Optional[str] = None
    IrradianceSourceAlias: Optional[str] = None
    TempMethodAlias: Optional[str] = None
    TempSourceAlias: Optional[str] = None
    TempUnit: Optional[str] = None
    IrlTimeUtc: Optional[str] = None
    SkyClaritySourceAlias: Optional[str] = None
    IrradianceMethodAlias: Optional[str] = None
    OpaqueCloudCoveragePercents: Optional[List[int]] = None
    IrradianceWPerM2: Optional[List[int]] = None
    Temperatures: Optional[List[float]] = None
    WorldInstanceAlias: Optional[str] = None
    MpAlias: str = "r.weather.forecast.1_0_0"

    def asdict(self):
        d = self._asdict()
        if d["WorldInstanceAlias"] is None:
            del d["WorldInstanceAlias"]
        if d["SkyClarityMethodAlias"] is None:
            del d["SkyClarityMethodAlias"]
        if d["IrradianceType"] is None:
            del d["IrradianceType"]
        if d["IrradianceSourceAlias"] is None:
            del d["IrradianceSourceAlias"]
        if d["TempMethodAlias"] is None:
            del d["TempMethodAlias"]
        if d["TempSourceAlias"] is None:
            del d["TempSourceAlias"]
        if d["OpaqueCloudCoveragePercents"] is None:
            del d["OpaqueCloudCoveragePercents"]
        if d["IrradianceWPerM2"] is None:
            del d["IrradianceWPerM2"]
        if d["TempUnit"] is None:
            del d["TempUnit"]
        if d["IrlTimeUtc"] is None:
            del d["IrlTimeUtc"]
        if d["SkyClaritySourceAlias"] is None:
            del d["SkyClaritySourceAlias"]
        if d["IrradianceMethodAlias"] is None:
            del d["IrradianceMethodAlias"]
        if d["Temperatures"] is None:
            del d["Temperatures"]
        return d

    def passes_derived_validations(self) -> Tuple[bool, Optional[List[str]]]:
        is_valid = True
        errors = []
        if self.MpAlias != "r.weather.forecast.1_0_0":
            is_valid = False
            errors.append(
                f"Payload requires MpAlias of r.weather.forecast.1_0_0, not {self.MpAlias}."
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
        if not isinstance(self.FromGNodeAlias, str):
            is_valid = False
            errors.append(f"FromGNodeAlias {self.FromGNodeAlias} must have type str.")
        if not property_format.is_lrd_alias_format(self.FromGNodeAlias):
            is_valid = False
            errors.append(
                f"FromGNodeAlias {self.FromGNodeAlias} must have format GNodeLrdAliasFormat."
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
        if not isinstance(self.WeatherUid, str):
            is_valid = False
            errors.append(f"WeatherUid {self.WeatherUid} must have type str.")
        if not property_format.is_uuid_canonical_textual(self.WeatherUid):
            is_valid = False
            errors.append(
                f"WeatherUid {self.WeatherUid} must have format UuidCanonicalTextual."
            )
        if not isinstance(self.StartMonthUtc, int):
            is_valid = False
            errors.append(f"StartMonthUtc {self.StartMonthUtc} must have type int.")
        if not isinstance(self.StartDayUtc, int):
            is_valid = False
            errors.append(f"StartDayUtc {self.StartDayUtc} must have type int.")
        if not isinstance(self.StartHourUtc, int):
            is_valid = False
            errors.append(f"StartHourUtc {self.StartHourUtc} must have type int.")
        if not isinstance(self.ForecastUnixTimeS, int):
            is_valid = False
            errors.append(
                f"ForecastUnixTimeS {self.ForecastUnixTimeS} must have type int."
            )
        if not property_format.is_non_negative_int64(self.ForecastUnixTimeS):
            is_valid = False
            errors.append(
                f"ForecastUnixTimeS {self.ForecastUnixTimeS} must have format NonNegativeInt64."
            )
        if not isinstance(self.StartMinuteUtc, int):
            is_valid = False
            errors.append(f"StartMinuteUtc {self.StartMinuteUtc} must have type int.")
        if not 0 <= self.StartMinuteUtc <= 60:
            is_valid = False
            errors.append("StartMinuteUtc must be in 0..59")
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
        if not isinstance(self.Comment, str):
            is_valid = False
            errors.append(f"Comment {self.Comment} must have type str.")
        if not isinstance(self.TimezoneString, str):
            is_valid = False
            errors.append(f"TimezoneString {self.TimezoneString} must have type str.")
        if not property_format.is_recognized_timezone_string(self.TimezoneString):
            is_valid = False
            errors.append(
                f"TimezoneString {self.TimezoneString} must have format RecognizedTimezoneString."
            )
        if not isinstance(self.LocationAlias, str):
            is_valid = False
            errors.append(f"LocationAlias {self.LocationAlias} must have type str.")
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
        if self.OpaqueCloudCoveragePercents:
            if not isinstance(self.OpaqueCloudCoveragePercents, list):
                is_valid = False
                errors.append(
                    f"OpaqueCloudCoveragePercents {self.OpaqueCloudCoveragePercents} must have type list."
                )
        if self.IrradianceWPerM2:
            if not isinstance(self.IrradianceWPerM2, list):
                is_valid = False
                errors.append(
                    f"IrradianceWPerM2 {self.IrradianceWPerM2} must have type list."
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
        if self.Temperatures:
            if not isinstance(self.Temperatures, list):
                is_valid = False
                errors.append(f"Temperatures {self.Temperatures} must have type list.")
        return is_valid, errors
