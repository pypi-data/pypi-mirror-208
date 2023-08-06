import csv
import datetime
import time
import uuid
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Tuple

import numpy as np
import pendulum
from gridworks.errors import DcError
from gridworks.errors import SchemaError

import gwatn.types.hack_property_format as property_format
from gwatn.types.hack_utils import log_style_utc_date_w_millis
from gwatn.types.ws_forecast_gnode.r_weather_forecast_sync.r_weather_forecast_sync_1_0_0 import (
    Payload as RWeatherForecastSync100Payload,
)
from gwatn.types.ws_forecast_gnode.r_weather_forecast_sync.r_weather_forecast_sync_1_0_0 import (
    R_Weather_Forecast_Sync_1_0_0,
)


class Payload(NamedTuple):
    LocationAlias: str
    Comment: str
    StartYearUtc: int
    StartMonthUtc: int
    StartDayUtc: int
    StartHourUtc: int
    UniformSliceDurationHrs: float
    TimezoneString: str
    WeatherUid: str
    MessageId: str
    TempUnit: Optional[str]
    ForecastUnixTimeS: int
    IrradianceType: Optional[str] = None
    TempSourceAlias: Optional[str] = None
    TempMethodAlias: Optional[str] = None
    IrradianceSourceAlias: Optional[str] = None
    IrradianceMethodAlias: Optional[str] = None
    SkyClaritySourceAlias: Optional[str] = None
    SkyClarityMethodAlias: Optional[str] = None
    Temperatures: Optional[list] = None
    IrradianceWPerM2: Optional[List[int]] = None
    OpaqueCloudCoveragePercents: Optional[List[int]] = None
    WorldInstanceAlias: Optional[str] = None
    MpAlias: str = "csv.weather.forecast.sync.1_0_0"

    def asdict(self):
        d = self._asdict()
        if d["WorldInstanceAlias"] is None:
            del d["WorldInstanceAlias"]
        if d["IrradianceType"] is None:
            del d["IrradianceType"]
        if d["IrradianceSourceAlias"] is None:
            del d["IrradianceSourceAlias"]
        if d["SkyClarityMethodAlias"] is None:
            del d["SkyClarityMethodAlias"]
        if d["TempSourceAlias"] is None:
            del d["TempSourceAlias"]
        if d["TempMethodAlias"] is None:
            del d["TempMethodAlias"]
        if d["IrradianceWPerM2"] is None:
            del d["IrradianceWPerM2"]
        if d["TempUnit"] is None:
            del d["TempUnit"]
        if d["SkyClaritySourceAlias"] is None:
            del d["SkyClaritySourceAlias"]
        if d["IrradianceMethodAlias"] is None:
            del d["IrradianceMethodAlias"]
        if d["OpaqueCloudCoveragePercents"] is None:
            del d["OpaqueCloudCoveragePercents"]
        if d["Temperatures"] is None:
            del d["Temperatures"]
        return d

    def is_valid(self) -> Tuple[bool, Optional[List[str]]]:
        is_valid, errors = self.passes_derived_validations()
        return is_valid, errors

    def passes_derived_validations(self) -> Tuple[bool, Optional[List[str]]]:
        is_valid = True
        errors = []
        if self.MpAlias != "csv.weather.forecast.sync.1_0_0":
            is_valid = False
            errors.append(
                f"Payload requires MpAlias of 'csv.weather.forecast.sync.1_0_0', not {self.MpAlias}."
            )
        if not isinstance(self.LocationAlias, str):
            is_valid = False
            errors.append(f"LocationAlias must have type str.")
        if not isinstance(self.StartYearUtc, int):
            is_valid = False
            errors.append(f"StartYearUtc must have type int.")
        if not isinstance(self.StartMonthUtc, int):
            is_valid = False
            errors.append(f"StartMonthUtc must have type int.")
        if not isinstance(self.StartDayUtc, int):
            is_valid = False
            errors.append(f"StartDayUtc must have type int.")
        if not isinstance(self.StartHourUtc, int):
            is_valid = False
            errors.append(f"StartHourUtc must have type int.")
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
        if not isinstance(self.UniformSliceDurationHrs, float):
            is_valid = False
            errors.append(f"UniformSliceDurationHrs must have type float.")
        if not isinstance(self.TimezoneString, str):
            is_valid = False
            errors.append(f"TimezoneString {self.TimezoneString} must have type str.")
        if not isinstance(self.WeatherUid, str):
            is_valid = False
            errors.append(f"WeatherUid {self.WeatherUid} must have type str.")
        if not property_format.is_uuid_canonical_textual(self.WeatherUid):
            is_valid = False
            errors.append(
                f"WeatherUid {self.WeatherUid} must have format UuidCanonicalTextual."
            )
        if not isinstance(self.MessageId, str):
            is_valid = False
            errors.append(f"MessageId {self.MessageId} must have type str.")
        if not property_format.is_uuid_canonical_textual(self.MessageId):
            is_valid = False
            errors.append(
                f"MessageId {self.MessageId} must have format UuidCanonicalTextual."
            )
        if not isinstance(self.ForecastUnixTimeS, int):
            is_valid = False
            errors.append(f"ForecastUnixTimeS most have type int")
        if not property_format.is_non_negative_int64(self.ForecastUnixTimeS):
            is_valid = False
            errors.append("ForecastUnixTimeS must have format NonNegativeInt64")
        if self.TempUnit:
            if not isinstance(self.TempUnit, str):
                is_valid = False
                errors.append(f"TempUnit {self.TempUnit} must have type str.")
            if not property_format.is_recognized_temperature_unit(self.TempUnit):
                is_valid = False
                errors.append(
                    f"TempUnit {self.TempUnit} must have format RecognizedTempUnit."
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
        if self.TempSourceAlias:
            if not isinstance(self.TempSourceAlias, str):
                is_valid = False
                errors.append(f"TempSourceAlias must have type str.")
            if not property_format.is_weather_source(self.TempSourceAlias):
                is_valid = False
                errors.append(
                    f"TempSourceAlias {self.TempSourceAlias} must have format WeatherSourceAlias."
                )
        if self.TempMethodAlias:
            if not isinstance(self.TempMethodAlias, str):
                is_valid = False
                errors.append(f"TempMethodAlias must have type str.")
            if not property_format.is_weather_method(self.TempMethodAlias):
                is_valid = False
                errors.append(
                    f"TempMethodAlias {self.TempMethodAlias} must have format WeatherMethodAlias."
                )
        if self.SkyClaritySourceAlias:
            if not isinstance(self.SkyClaritySourceAlias, str):
                is_valid = False
                errors.append(f"SkyClaritySourceAlias must have type str.")
            if not property_format.is_weather_source(self.SkyClaritySourceAlias):
                is_valid = False
                errors.append(
                    f"SkyClaritySourceAlias {self.SkyClaritySourceAlias} must have format WeatherSourceAlias."
                )
        if self.SkyClarityMethodAlias:
            if not isinstance(self.SkyClarityMethodAlias, str):
                is_valid = False
                errors.append(f"SkyClarityMethodAlias must have type str.")
            if not property_format.is_weather_method(self.SkyClarityMethodAlias):
                is_valid = False
                errors.append(
                    f"SkyClarityMethodAlias {self.SkyClarityMethodAlias} must have format WeatherMethodAlias."
                )
        if self.IrradianceSourceAlias:
            if not isinstance(self.IrradianceSourceAlias, str):
                is_valid = False
                errors.append(f"IrradianceSourceAlias must have type str.")
            if not property_format.is_weather_source(self.IrradianceSourceAlias):
                is_valid = False
                errors.append(
                    f"IrradianceSourceAlias {self.IrradianceSourceAlias} must have format WeatherSourceAlias."
                )
        if self.IrradianceMethodAlias:
            if not isinstance(self.IrradianceMethodAlias, str):
                is_valid = False
                errors.append(f"IrradianceMethodAlias must have type str.")
            if not property_format.is_weather_method(self.IrradianceMethodAlias):
                is_valid = False
                errors.append(
                    f"IrradianceMethodAlias {self.IrradianceMethodAlias} must have format WeatherMethodAlias."
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

        return is_valid, errors


class Csv_Weather_Forecast_Sync_1_0_0:
    mp_alias = "csv.weather.forecast.sync.1_0_0"

    @classmethod
    def payload_is_valid(
        cls, payload_as_dict: Dict[str, Any]
    ) -> Tuple[bool, Optional[List[str]]]:
        try:
            payload_as_dict["UniformSliceDurationHrs"] = float(
                payload_as_dict["UniformSliceDurationHrs"]
            )
        except ValueError:
            pass  # This will get caught in is_valid() check below
        if "TempUnit" not in payload_as_dict.keys():
            payload_as_dict["TempUnit"] = None
        if "TempSourceAlias" not in payload_as_dict.keys():
            payload_as_dict["TempSourceAlias"] = None
        if "TempMethodAlias" not in payload_as_dict.keys():
            payload_as_dict["TempMethodAlias"] = None
        if "IrradianceType" not in payload_as_dict.keys():
            payload_as_dict["IrradianceType"] = None
        if "IrradianceSourceAlias" not in payload_as_dict.keys():
            payload_as_dict["IrradianceSourceAlias"] = None
        if "IrradianceMethodAlias" not in payload_as_dict.keys():
            payload_as_dict["IrradianceMethodAlias"] = None
        if "SkyClaritySourceAlias" not in payload_as_dict.keys():
            payload_as_dict["SkyClaritySourceAlias"] = None
        if "SkyClarityMethodAlias" not in payload_as_dict.keys():
            payload_as_dict["SkyClarityMethodAlias"] = None
        if "Temperatures" not in payload_as_dict.keys():
            payload_as_dict["Temperatures"] = None
        if "IrradianceWPerM2" not in payload_as_dict.keys():
            payload_as_dict["IrradianceWPerM2"] = None
        if "OpaqueCloudCoveragePercents" not in payload_as_dict.keys():
            payload_as_dict["OpaqueCloudCoveragePercents"] = None
        if "WorldInstanceAlias" not in payload_as_dict.keys():
            payload_as_dict["WorldInstanceAlias"] = None

        try:
            p = Payload(
                MpAlias=payload_as_dict["MpAlias"],
                LocationAlias=payload_as_dict["LocationAlias"],
                Comment=payload_as_dict["Comment"],
                StartYearUtc=payload_as_dict["StartYearUtc"],
                StartMonthUtc=payload_as_dict["StartMonthUtc"],
                StartDayUtc=payload_as_dict["StartDayUtc"],
                StartHourUtc=payload_as_dict["StartHourUtc"],
                UniformSliceDurationHrs=payload_as_dict["UniformSliceDurationHrs"],
                TimezoneString=payload_as_dict["TimezoneString"],
                ForecastUnixTimeS=payload_as_dict["ForecastUnixTimeS"],
                WeatherUid=payload_as_dict["WeatherUid"],
                MessageId=payload_as_dict["MessageId"],
                TempUnit=payload_as_dict["TempUnit"],
                IrradianceType=payload_as_dict["IrradianceType"],
                TempSourceAlias=payload_as_dict["TempSourceAlias"],
                TempMethodAlias=payload_as_dict["TempMethodAlias"],
                IrradianceSourceAlias=payload_as_dict["IrradianceSourceAlias"],
                IrradianceMethodAlias=payload_as_dict["IrradianceMethodAlias"],
                SkyClaritySourceAlias=payload_as_dict["SkyClaritySourceAlias"],
                SkyClarityMethodAlias=payload_as_dict["SkyClarityMethodAlias"],
                Temperatures=payload_as_dict["Temperatures"],
                IrradianceWPerM2=payload_as_dict["IrradianceWPerM2"],
                OpaqueCloudCoveragePercents=payload_as_dict[
                    "OpaqueCloudCoveragePercents"
                ],
                WorldInstanceAlias=payload_as_dict["WorldInstanceAlias"],
            )
        except TypeError:
            errors = [TypeError]
            return False, errors
        return p.is_valid()

    def __init__(self, weather_csv, world_instance_alias=None):
        self.errors = []
        self.payload = None
        first_data_row = 22
        temperatures = []
        irradiances = []
        sky_clarities = []
        uniform_slice_duration_hrs = np.array([])
        with open(weather_csv, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            line_idx = 0
            for row in reader:
                if line_idx == 0:
                    property = row[0].replace("\ufeff", "")
                    mp_alias = row[1]
                    if property != "MpAlias":
                        raise Exception(
                            f"Csv 0,0 must be MpAlias, instead it is {property}"
                        )
                    if mp_alias != "csv.weather.forecast.sync.1_0_0":
                        raise Exception(
                            f"MpAlias for {weather_csv} must be csv.weather.forecast.sync.1_0_0. Instead it was {mp_alias}"
                        )
                if line_idx == 1:
                    property = row[0]
                    location_alias = row[1].strip()
                    if property != "LocationAlias":
                        raise Exception(
                            f"Csv 1,0 must be LocationAlias, instead it is {property}"
                        )
                if line_idx == 2:
                    property = row[0]
                    if len(row) == 1:
                        temp_source_alias = None
                    else:
                        temp_source_alias = row[1].strip()
                        if temp_source_alias == "":
                            temp_source_alias = None
                    if property != "TempSourceAlias":
                        raise Exception(
                            f"Csv 2,0 must be TempSourceAlias, instead it is {property}"
                        )
                if line_idx == 3:
                    property = row[0]
                    temp_method_alias = row[1].strip()
                    if len(row) == 1:
                        temp_method_alias = None
                    else:
                        if temp_method_alias == "":
                            temp_method_alias = None
                    if property != "TempMethodAlias":
                        raise Exception(
                            f"Csv 3,0 must be TempMethodAlias, instead it is {property}"
                        )
                if line_idx == 4:
                    property = row[0]
                    if len(row) == 1:
                        sky_clarity_source_alias = None
                    else:
                        sky_clarity_source_alias = row[1].strip()
                        if sky_clarity_source_alias == "":
                            sky_clarity_source_alias = None
                    if property != "SkyClaritySourceAlias":
                        raise Exception(
                            f"Csv 4,0 must be SkyClaritySourceAlias, instead it is {property}"
                        )
                if line_idx == 5:
                    property = row[0]
                    if len(row) == 1:
                        sky_clarity_method_alias = None
                    else:
                        sky_clarity_method_alias = row[1].strip()
                        if sky_clarity_method_alias == "":
                            sky_clarity_method_alias = None
                    if property != "SkyClarityMethodAlias":
                        raise Exception(
                            f"Csv 5,0 must be SkyClarityMethodAlias, instead it is {property}"
                        )
                if line_idx == 6:
                    property = row[0]
                    if len(row) == 1:
                        irradiance_source_alias = None
                    else:
                        irradiance_source_alias = row[1].strip()
                        if irradiance_source_alias == "":
                            irradiance_source_alias = None
                    if property != "IrradianceSourceAlias":
                        raise Exception(
                            f"Csv 6,0 of {weather_csv} must be IrradianceSourceAlias, instead it is {property}"
                        )
                if line_idx == 7:
                    property = row[0]
                    if len(row) == 1:
                        irradiance_method_alias = None
                    else:
                        irradiance_method_alias = row[1].strip()
                        if irradiance_method_alias == "":
                            irradiance_method_alias = None
                    if property != "IrradianceMethodAlias":
                        raise Exception(
                            f"Csv 7,0 must be IrradianceMethodAlias, instead it is {property}"
                        )
                if line_idx == 8:
                    property = row[0]
                    comment = row[1].strip()
                    if property != "Comment":
                        raise Exception(
                            f"Csv 8,0 must be Comment, instead it is {property}"
                        )
                if line_idx == 9:
                    property = row[0]
                    start_year_utc = int(row[1])
                    if property != "StartYearUtc":
                        raise Exception(
                            f"Csv 9,0 must be StartYearUtc, instead it is {property}"
                        )
                if line_idx == 10:
                    property = row[0]
                    start_month_utc = int(row[1])
                    if property != "StartMonthUtc":
                        raise Exception(
                            f"Csv 10,0 must be StartMonthUtc, instead it is {property}"
                        )
                if line_idx == 11:
                    property = row[0]
                    start_day_utc = int(row[1])
                    if property != "StartDayUtc":
                        raise Exception(
                            f"Csv 11,0 must be StartDayUtc, instead it is {property}"
                        )
                if line_idx == 12:
                    property = row[0]
                    start_hour_utc = int(row[1])
                    if property != "StartHourUtc":
                        raise Exception(
                            f"Csv 12,0 must be StartHourUtc, instead it is {property}"
                        )
                if line_idx == 13:
                    property = row[0]
                    uniform_slice_duration_hrs = float(row[1])
                    if property != "UniformSliceDurationHrs":
                        raise Exception(
                            f"Csv 13,0 must be UniformSliceDurationHrs, instead it is {property}"
                        )
                if line_idx == 14:
                    property = row[0]
                    timezone_string = row[1].strip()
                    if property != "TimezoneString":
                        raise Exception(
                            f"Csv 14,0 must be TimezoneString, instead it is {property}"
                        )
                if line_idx == 15:
                    property = row[0]
                    if len(row) == 1:
                        temp_unit = None
                    else:
                        temp_unit = row[1].strip()
                        if temp_unit == "":
                            temp_unit = None
                    if property != "TempUnit":
                        raise Exception(
                            f"Csv 15,0 must be TempUnit, instead it is {property}"
                        )
                if line_idx == 16:
                    property = row[0]
                    if len(row) == 1:
                        irradiance_type = None
                    else:
                        irradiance_type = row[1].strip()
                        if irradiance_type == "":
                            irradiance_type = None
                    if property != "IrradianceType":
                        raise Exception(
                            f"Csv 16,0 must be IrradianceType, instead it is {property}"
                        )
                if line_idx == 17:
                    property = row[0]
                    include_temp_str = row[1].strip()
                    if property != "IncludeTemp":
                        raise Exception(
                            f"Csv 17,0 must be IncludeTemp, instead it is {property}"
                        )
                    if include_temp_str == "True":
                        include_temp = True
                    else:
                        include_temp = False
                if line_idx == 18:
                    property = row[0]
                    include_irradiance_str = row[1].strip()
                    if property != "IncludeIrradiance":
                        raise Exception(
                            f"Csv 18,0 must be IncludeIrradiance, instead it is {property}"
                        )
                    if include_irradiance_str == "True":
                        include_irradiance = True
                    else:
                        include_irradiance = False
                if line_idx == 19:
                    property = row[0]
                    include_sky_clarity_str = row[1].strip()
                    if property != "IncludeSkyClarity":
                        raise Exception(
                            f"Csv 19,0 must be IncludeSkyClarity, instead it is {property}"
                        )
                    if include_sky_clarity_str == "True":
                        include_sky_clarity = True
                    else:
                        include_sky_clarity = False
                if line_idx == 20:
                    property = row[0]
                    forecast_unix_time_s = int(row[1])
                    if property != "ForecastUnixTimeS":
                        raise Exception(
                            f"Csv 20,0 must be ForecastUnixTimeS, instead it is {property}"
                        )
                if line_idx == 21:
                    property = row[0]
                    price_uid = row[1].strip()
                    if property != "WeatherUid":
                        raise Exception(
                            f"Csv 21,0 must be WeatherUid, instead it is {property}"
                        )
                if line_idx == 22:
                    header0 = row[0].strip()
                    header1 = row[1].strip()
                    header2 = row[2].strip()
                    if header0 != "Temperatures":
                        raise Exception(
                            f"Csv 22,0 must be Temperatures, instead it is {header0}"
                        )
                    if header1 != "IrradianceWPerM2":
                        raise Exception(
                            f"Csv 22,1 must be IrradianceWPerM2, instead it is {header1}"
                        )
                    if header2 != "OpaqueCloudCoveragePercents":
                        raise Exception(
                            f"Csv 22,2 must be OpaqueCloudCoveragePercents, instead it is {header2}"
                        )
                elif line_idx >= first_data_row:
                    if include_temp:
                        try:
                            temperatures.append(int(row[0]))
                        except ValueError:
                            raise Exception(
                                f"File {weather_csv} Missing a temperature in row {line_idx+1}"
                            )
                    if include_irradiance:
                        try:
                            irradiances.append(int(row[1]))
                        except ValueError:
                            raise Exception(
                                f"Missing an irradiance in row {line_idx+1}"
                            )
                    if include_sky_clarity:
                        try:
                            sky_clarities.append(int(row[2]))
                        except ValueError:
                            raise Exception(f"Missing an occp in row {line_idx+1}")
                line_idx += 1
        if not include_temp:
            temperatures = None
            temp_unit = None
        if not include_irradiance:
            irradiances = None
            irradiance_type = None
        if not include_sky_clarity:
            sky_clarities = None

        p = Payload(
            LocationAlias=location_alias,
            Comment=comment,
            StartYearUtc=start_year_utc,
            StartMonthUtc=start_month_utc,
            StartDayUtc=start_day_utc,
            StartHourUtc=start_hour_utc,
            UniformSliceDurationHrs=uniform_slice_duration_hrs,
            TimezoneString=timezone_string,
            ForecastUnixTimeS=forecast_unix_time_s,
            WeatherUid=price_uid,
            MessageId=str(uuid.uuid4()),
            TempUnit=temp_unit,
            IrradianceType=irradiance_type,
            TempSourceAlias=temp_source_alias,
            TempMethodAlias=temp_method_alias,
            IrradianceSourceAlias=irradiance_source_alias,
            IrradianceMethodAlias=irradiance_method_alias,
            SkyClaritySourceAlias=sky_clarity_source_alias,
            SkyClarityMethodAlias=sky_clarity_method_alias,
            Temperatures=temperatures,
            IrradianceWPerM2=irradiances,
            OpaqueCloudCoveragePercents=sky_clarities,
            WorldInstanceAlias=world_instance_alias,
        )

        is_valid, errors = p.is_valid()
        # if is_valid is False:
        #    self.errors = errors
        #    print(errors)
        #    raise SchemaError(f"Failed to create payload due to these errors:{errors}. Input file is {weather_csv}")
        # else:
        self.payload = p

    def paired_rabbit_payload(self, agent) -> RWeatherForecastSync100Payload:
        start_utc = pendulum.datetime(
            year=self.payload.StartYearUtc,
            month=self.payload.StartMonthUtc,
            day=self.payload.StartDayUtc,
            hour=self.payload.StartHourUtc,
        )

        return R_Weather_Forecast_Sync_1_0_0(
            agent=agent,
            uniform_slice_duration_hrs=self.payload.UniformSliceDurationHrs,
            location_alias=self.payload.LocationAlias,
            start_utc=start_utc,
            weather_uid=self.payload.WeatherUid,
            timezone_string=self.payload.TimezoneString,
            forecast_unix_time_s=self.payload.ForecastUnixTimeS,
            comment=self.payload.Comment,
            irradiance_type=self.payload.IrradianceType,
            irradiance_method_alias=self.payload.IrradianceMethodAlias,
            irradiance_source_alias=self.payload.IrradianceSourceAlias,
            sky_clarity_method_alias=self.payload.SkyClarityMethodAlias,
            sky_clarity_source_alias=self.payload.SkyClaritySourceAlias,
            temp_method_alias=self.payload.TempMethodAlias,
            temp_source_alias=self.payload.TempSourceAlias,
            irradiance_w_per_m2=self.payload.IrradianceWPerM2,
            opaque_cloud_coverage_percents=self.payload.OpaqueCloudCoveragePercents,
            temperatures=self.payload.Temperatures,
            temp_unit=self.payload.TempUnit,
        ).payload
