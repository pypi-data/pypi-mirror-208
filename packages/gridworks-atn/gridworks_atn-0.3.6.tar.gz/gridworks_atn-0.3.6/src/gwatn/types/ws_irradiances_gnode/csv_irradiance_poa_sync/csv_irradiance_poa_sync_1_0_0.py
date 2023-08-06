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
from gridworks.errors import DcError
from gridworks.errors import SchemaError

import gwatn.types.hack_property_format as property_format
from gwatn.enums import RecognizedIrradianceType
from gwatn.types.hack_type_base import HackTypeBase
from gwatn.types.hack_utils import camel_to_snake
from gwatn.types.hack_utils import log_style_utc_date_w_millis
from gwatn.types.hack_utils import snake_to_camel
from gwatn.types.ws_forecast_gnode.r_weather_forecast_sync.r_weather_forecast_sync_1_0_0 import (
    Payload as PairedRabbitPayload,
)


class Payload(NamedTuple):
    MpAlias: str
    WorldInstanceAlias: str
    LocationAlias: str
    SourceAlias: str
    MethodAlias: str
    Comment: str
    StartYearUtc: int
    StartMonthUtc: int
    StartDayUtc: int
    StartHourUtc: int
    StartMinuteUtc: int
    UniformSliceDurationHrs: float
    TimezoneString: str
    WeatherUid: str
    Header: str
    IrradiancePoaWPerM2: list
    MessageId: str

    def asdict(self):
        d = self._asdict()
        return d

    def is_valid(self) -> Tuple[bool, Optional[List[str]]]:
        is_valid, errors = self.passes_derived_validations()
        return is_valid, errors

    def passes_derived_validations(self) -> Tuple[bool, Optional[List[str]]]:
        is_valid = True
        errors = []
        if self.MpAlias != "csv.irradiance.poa.sync.1_0_0":
            is_valid = False
            errors.append(
                f"Payload requires MpAlias of 'csv.irradiance.poa.sync.1_0_0', not {self.MpAlias}."
            )
        if not isinstance(self.WorldInstanceAlias, str):
            is_valid = False
            errors.append(
                f"WorldInstanceAlias {self.WorldInstanceAlias} must have type str."
            )
        if not property_format.is_world_instance_alias_format(self.WorldInstanceAlias):
            is_valid = False
            errors.append(
                f"WorldInstanceAlias {self.WorldInstanceAlias} must have format WorldInstanceAliasFormat"
            )
        if not isinstance(self.LocationAlias, str):
            is_valid = False
            errors.append(f"LocationAlias must have type str.")
        if not isinstance(self.SourceAlias, str):
            is_valid = False
            errors.append(f"SourceAlias must have type str.")
        if not property_format.is_weather_source(self.SourceAlias):
            is_valid = False
            errors.append(
                f"SourceAlias {self.SourceAlias} must have format WeatherSourceAlias."
            )
        if not isinstance(self.MethodAlias, str):
            is_valid = False
            errors.append(f"MethodAlias must have type str.")
        if not property_format.is_weather_method(self.MethodAlias):
            is_valid = False
            errors.append(
                f"MethodAlias {self.MethodAlias} must have format WeatherMethodAlias."
            )
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
        if not isinstance(self.StartMinuteUtc, int):
            is_valid = False
            errors.append(f"StartMinuteUtc must have type int.")
        try:
            datetime.datetime(
                year=self.StartYearUtc,
                month=self.StartMonthUtc,
                day=self.StartDayUtc,
                hour=self.StartHourUtc,
                minute=self.StartMinuteUtc,
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
        # TODO: add rest of validations

        return is_valid, errors


class Csv_Irradiance_Poa_Sync_1_0_0:
    mp_alias = "csv.irradiance.poa.sync.1_0_0"

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
        try:
            p = Payload(
                MpAlias=payload_as_dict["MpAlias"],
                WorldInstanceAlias=payload_as_dict["WorldInstanceAlias"],
                LocationAlias=payload_as_dict["LocationAlias"],
                SourceAlias=payload_as_dict["SourceAlias"],
                MethodAlias=payload_as_dict["MethodAlias"],
                Comment=payload_as_dict["Comment"],
                StartYearUtc=payload_as_dict["StartYearUtc"],
                StartMonthUtc=payload_as_dict["StartMonthUtc"],
                StartDayUtc=payload_as_dict["StartDayUtc"],
                StartHourUtc=payload_as_dict["StartHourUtc"],
                StartMinuteUtc=payload_as_dict["StartMinuteUtc"],
                UniformSliceDurationHrs=payload_as_dict["UniformSliceDurationHrs"],
                TimezoneString=payload_as_dict["TimezoneString"],
                WeatherUid=payload_as_dict["WeatherUid"],
                Header=payload_as_dict["Header"],
                Temperatures=payload_as_dict["Temperatures"],
                MessageId=payload_as_dict["MessageId"],
            )
        except TypeError:
            errors = [TypeError]
            return False, errors
        return p.is_valid()

    def __init__(self, irradiance_csv):
        self.errors = []
        self.payload = None
        first_data_row = 14
        irradiances = []
        uniform_slice_duration_hrs = np.array([])
        with open(irradiance_csv, newline="") as csvfile:
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
                if line_idx == 1:
                    property = row[0]
                    location_alias = row[1].strip()
                    if property != "LocationAlias":
                        raise Exception(
                            f"Csv 1,0 must be LocationAlias, instead it is {property}"
                        )
                if line_idx == 2:
                    property = row[0]
                    source_alias = row[1].strip()
                    if property != "SourceAlias":
                        raise Exception(
                            f"Csv 2,0 must be SourceAlias, instead it is {property}"
                        )
                if line_idx == 3:
                    property = row[0]
                    method_alias = row[1].strip()
                    if property != "MethodAlias":
                        raise Exception(
                            f"Csv 3,0 must be MethodAlias, instead it is {property}"
                        )
                if line_idx == 4:
                    property = row[0]
                    comment = row[1].strip()
                    if property != "Comment":
                        raise Exception(
                            f"Csv 4,0 must be Comment, instead it is {property}"
                        )
                if line_idx == 5:
                    property = row[0]
                    start_year_utc = int(row[1])
                    if property != "StartYearUtc":
                        raise Exception(
                            f"Csv 5,0 must be StartYearUtc, instead it is {property}"
                        )
                if line_idx == 6:
                    property = row[0]
                    start_month_utc = int(row[1])
                    if property != "StartMonthUtc":
                        raise Exception(
                            f"Csv 6,0 must be StartMonthUtc, instead it is {property}"
                        )
                if line_idx == 7:
                    property = row[0]
                    start_day_utc = int(row[1])
                    if property != "StartDayUtc":
                        raise Exception(
                            f"Csv 7,0 must be StartDayUtc, instead it is {property}"
                        )
                if line_idx == 8:
                    property = row[0]
                    start_hour_utc = int(row[1])
                    if property != "StartHourUtc":
                        raise Exception(
                            f"Csv 8,0 must be StartHourUtc, instead it is {property}"
                        )
                if line_idx == 9:
                    property = row[0]
                    start_minute_utc = int(row[1])
                    if property != "StartMinuteUtc":
                        raise Exception(
                            f"Csv 9,0 must be StartMinuteUtc, instead it is {property}"
                        )
                if line_idx == 10:
                    property = row[0]
                    uniform_slice_duration_hrs = float(row[1])
                    if property != "UniformSliceDurationHrs":
                        raise Exception(
                            f"Csv 10,0 must be UniformSliceDurationHrs, instead it is {property}"
                        )
                if line_idx == 11:
                    property = row[0]
                    timezone_string = row[1].strip()
                    if property != "TimezoneString":
                        raise Exception(
                            f"Csv 11,0 must be TimezoneString, instead it is {property}"
                        )
                if line_idx == 12:
                    property = row[0]
                    price_uid = row[1].strip()
                    if property != "WeatherUid":
                        raise Exception(
                            f"Csv 12,0 must be WeatherUid, instead it is {property}"
                        )
                if line_idx == 13:
                    property = row[0]
                    header = row[1].strip()
                    if property != "Header":
                        raise Exception(
                            f"Csv 13,0 must be Header, instead it is {property}"
                        )
                    if header != "Clear Sky Plain of Array Irradiance (W/M2)":
                        raise Exception(
                            f"Csv 13,1 must be 'Clear Sky Plain of Array Irradiance (W/M2)', instead it is {header}"
                        )
                elif line_idx >= first_data_row:
                    try:
                        irradiances.append(int(row[0]))
                    except ValueError:
                        raise Exception(
                            f"Irradiance {row[0]} in row {line_idx+1} must be an int"
                        )

                line_idx += 1

        p = Payload(
            MpAlias=mp_alias,
            WorldInstanceAlias="dw1__1",
            LocationAlias=location_alias,
            SourceAlias=source_alias,
            MethodAlias=method_alias,
            Comment=comment,
            StartYearUtc=start_year_utc,
            StartMonthUtc=start_month_utc,
            StartDayUtc=start_day_utc,
            StartHourUtc=start_hour_utc,
            StartMinuteUtc=start_minute_utc,
            UniformSliceDurationHrs=uniform_slice_duration_hrs,
            TimezoneString=timezone_string,
            WeatherUid=price_uid,
            Header=header,
            IrradiancePoaWPerM2=irradiances,
            MessageId=str(uuid.uuid4()),
        )

        is_valid, errors = p.is_valid()
        if is_valid is False:
            self.errors = errors
            print(errors)
            raise SchemaError(
                f"Failed to create payload due to these errors:{errors}. Input file is {irradiance_csv}"
            )
        else:
            self.payload = p

    def paired_rabbit_payload(
        self,
        world_instance_alias: str,
        from_g_node_alias: str,
        from_g_node_instance_id: str,
    ):
        p = PairedRabbitPayload(
            FromGNodeAlias=from_g_node_alias,
            FromGNodeInstanceId=from_g_node_instance_id,
            LocationAlias=self.payload.LocationAlias,
            IrradianceSourceAlias=self.payload.SourceAlias,
            IrradianceMethodAlias=self.payload.MethodAlias,
            IrradianceType=RecognizedIrradianceType.PlaneOfArray.value,
            Comment=self.payload.Comment,
            StartYearUtc=self.payload.StartYearUtc,
            StartMonthUtc=self.payload.StartMonthUtc,
            StartDayUtc=self.payload.StartDayUtc,
            StartHourUtc=self.payload.StartHourUtc,
            StartMinuteUtc=self.payload.StartMinuteUtc,
            UniformSliceDurationHrs=self.payload.UniformSliceDurationHrs,
            TimezoneString=self.payload.TimezoneString,
            WeatherUid=self.payload.WeatherUid,
            IrradianceWPerM2=self.payload.IrradiancePoaWPerM2,
            WorldInstanceAlias=world_instance_alias,
            MessageId=str(uuid.uuid4()),
            IrlTimeUtc=log_style_utc_date_w_millis(time.time()),
        )
        return p
