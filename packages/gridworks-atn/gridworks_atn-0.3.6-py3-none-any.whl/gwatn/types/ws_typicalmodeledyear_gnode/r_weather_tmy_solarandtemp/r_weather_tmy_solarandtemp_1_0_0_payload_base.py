"""PayloadBase for r.weather.tmy.solarandtemp.1_0_0"""
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
    TimezoneString: str  #
    WeatherUid: str  #
    Comment: str  #
    TempSourceAlias: str  #
    IrradianceSourceAlias: str  #
    TempUnit: str  #
    CreatedAtUnixS: int  #
    SkyClarityAlias: str  #
    IrradianceType: str  #
    IrradianceMethodAlias: str  #
    LocationAlias: str  #
    Temperatures: List[float]
    IrradianceWPerM2: List[int]
    OpaqueCloudCoveragePercents: List[int]
    TempMethodAlias: Optional[str] = None
    SkyClarityMethodAlias: Optional[str] = None
    IrlTimeUtc: Optional[str] = None
    WorldInstanceAlias: Optional[str] = None
    MpAlias: str = "r.weather.tmy.solarandtemp.1_0_0"

    def asdict(self):
        d = self._asdict()
        if d["WorldInstanceAlias"] is None:
            del d["WorldInstanceAlias"]
        if d["TempMethodAlias"] is None:
            del d["TempMethodAlias"]
        if d["SkyClarityMethodAlias"] is None:
            del d["SkyClarityMethodAlias"]
        if d["IrlTimeUtc"] is None:
            del d["IrlTimeUtc"]
        return d

    def passes_derived_validations(self) -> Tuple[bool, Optional[List[str]]]:
        is_valid = True
        errors = []
        if self.MpAlias != "r.weather.tmy.solarandtemp.1_0_0":
            is_valid = False
            errors.append(
                f"Payload requires MpAlias of r.weather.tmy.solarandtemp.1_0_0, not {self.MpAlias}."
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
        if not isinstance(self.TimezoneString, str):
            is_valid = False
            errors.append(f"TimezoneString {self.TimezoneString} must have type str.")
        if not property_format.is_recognized_timezone_string(self.TimezoneString):
            is_valid = False
            errors.append(
                f"TimezoneString {self.TimezoneString} must have format RecognizedTimezoneString."
            )
        if not isinstance(self.Temperatures, list):
            is_valid = False
            errors.append(f"Temperatures {self.Temperatures} must have type list.")
        else:
            for elt in self.Temperatures:
                if not isinstance(elt, float):
                    is_valid = False
                    errors.append(
                        f"Elements of the list Temperatures must have type float. Error with {elt}"
                    )
        if not isinstance(self.WeatherUid, str):
            is_valid = False
            errors.append(f"WeatherUid {self.WeatherUid} must have type str.")
        if not property_format.is_uuid_canonical_textual(self.WeatherUid):
            is_valid = False
            errors.append(
                f"WeatherUid {self.WeatherUid} must have format UuidCanonicalTextual."
            )
        if not isinstance(self.IrradianceWPerM2, list):
            is_valid = False
            errors.append(
                f"IrradianceWPerM2 {self.IrradianceWPerM2} must have type list."
            )
        else:
            for elt in self.IrradianceWPerM2:
                if not isinstance(elt, int):
                    is_valid = False
                    errors.append(
                        f"Elements of the list IrradianceWPerM2 must have type int. Error with {elt}"
                    )
        if not isinstance(self.Comment, str):
            is_valid = False
            errors.append(f"Comment {self.Comment} must have type str.")
        if not isinstance(self.TempSourceAlias, str):
            is_valid = False
            errors.append(f"TempSourceAlias {self.TempSourceAlias} must have type str.")
        if not property_format.is_weather_source(self.TempSourceAlias):
            is_valid = False
            errors.append(
                f"TempSourceAlias {self.TempSourceAlias} must have format WeatherSource."
            )
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
        if not isinstance(self.OpaqueCloudCoveragePercents, list):
            is_valid = False
            errors.append(
                f"OpaqueCloudCoveragePercents {self.OpaqueCloudCoveragePercents} must have type list."
            )
        else:
            for elt in self.OpaqueCloudCoveragePercents:
                if not isinstance(elt, int):
                    is_valid = False
                    errors.append(
                        f"Elements of the list OpaqueCloudCoveragePercents must have type int. Error with {elt}"
                    )
        if not isinstance(self.TempUnit, str):
            is_valid = False
            errors.append(f"TempUnit {self.TempUnit} must have type str.")
        if not property_format.is_recognized_temperature_unit(self.TempUnit):
            is_valid = False
            errors.append(
                f"TempUnit {self.TempUnit} must have format RecognizedTemperatureUnit."
            )
        if not isinstance(self.CreatedAtUnixS, int):
            is_valid = False
            errors.append(f"CreatedAtUnixS {self.CreatedAtUnixS} must have type int.")
        if not property_format.is_non_negative_int64(self.CreatedAtUnixS):
            is_valid = False
            errors.append(
                f"CreatedAtUnixS {self.CreatedAtUnixS} must have format NonNegativeInt64."
            )
        if not isinstance(self.SkyClarityAlias, str):
            is_valid = False
            errors.append(f"SkyClarityAlias {self.SkyClarityAlias} must have type str.")
        if not property_format.is_weather_source(self.SkyClarityAlias):
            is_valid = False
            errors.append(
                f"SkyClarityAlias {self.SkyClarityAlias} must have format WeatherSource."
            )
        if not isinstance(self.IrradianceType, str):
            is_valid = False
            errors.append(f"IrradianceType {self.IrradianceType} must have type str.")
        if not property_format.is_recognized_irradiance_type(self.IrradianceType):
            is_valid = False
            errors.append(
                f"IrradianceType {self.IrradianceType} must have format RecognizedIrradianceType."
            )
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
