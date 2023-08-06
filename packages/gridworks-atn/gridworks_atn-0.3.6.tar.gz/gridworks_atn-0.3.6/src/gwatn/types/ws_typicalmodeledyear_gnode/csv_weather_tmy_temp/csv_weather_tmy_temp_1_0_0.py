"""PayloadBase for csv.weather.tmy.temp.1_0_0"""
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

from gridworks.errors import SchemaError

import gwatn.types.hack_property_format as property_format
from gwatn.types.hack_utils import log_style_utc_date_w_millis
from gwatn.types.ws_typicalmodeledyear_gnode.r_weather_tmy_temp.r_weather_tmy_temp_1_0_0 import (
    Payload as PairedRabbitPayload,
)


class Payload(NamedTuple):
    LocationAlias: str  #
    SourceAlias: str  #
    MethodAlias: str
    Comment: str  #
    TimezoneString: str
    TempUnit: str  #
    CreatedAtUnixS: int  #
    WeatherUid: str  #
    MessageId: str
    Temperatures: List[int]
    WorldInstanceAlias: Optional[str] = None
    MpAlias: str = "csv.weather.tmy.temp.1_0_0"

    def asdict(self):
        d = self._asdict()
        if d["WorldInstanceAlias"] is None:
            del d["WorldInstanceAlias"]
        return d

    def is_valid(self) -> Tuple[bool, Optional[List[str]]]:
        is_valid, errors = self.passes_derived_validations()
        return is_valid, errors

    def passes_derived_validations(self) -> Tuple[bool, Optional[List[str]]]:
        is_valid = True
        errors = []
        if self.MpAlias != "csv.weather.tmy.temp.1_0_0":
            is_valid = False
            errors.append(
                f"Payload requires MpAlias of csv.weather.tmy.temp.1_0_0, not {self.MpAlias}."
            )
        if not isinstance(self.MessageId, str):
            is_valid = False
            errors.append(f"MessageId {self.MessageId} must have type str.")
        if not property_format.is_uuid_canonical_textual(self.MessageId):
            is_valid = False
            errors.append(
                f"MessageId {self.MessageId} must have format UuidCanonicalTextual."
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
        if not isinstance(self.Comment, str):
            is_valid = False
            errors.append(f"Comment {self.Comment} must have type str.")
        if not isinstance(self.LocationAlias, str):
            is_valid = False
            errors.append(f"LocationAlias {self.LocationAlias} must have type str.")
        if not isinstance(self.WeatherUid, str):
            is_valid = False
            errors.append(f"WeatherUid {self.WeatherUid} must have type str.")
        if not property_format.is_uuid_canonical_textual(self.WeatherUid):
            is_valid = False
            errors.append(
                f"WeatherUid {self.WeatherUid} must have format UuidCanonicalTextual."
            )
        if not isinstance(self.SourceAlias, str):
            is_valid = False
            errors.append(f"SourceAlias {self.SourceAlias} must have type str.")
        if not property_format.is_weather_source(self.SourceAlias):
            is_valid = False
            errors.append(
                f"SourceAlias {self.SourceAlias} must have format WeatherSource."
            )
        if not isinstance(self.Temperatures, list):
            is_valid = False
            errors.append(f"Temperatures {self.Temperatures} must have type list.")
        for elt in self.Temperatures:
            if not isinstance(elt, int):
                is_valid = False
                errors.append(
                    f"Elements of the list Temperatures must have type int. Error with {elt}"
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
        if not isinstance(self.MethodAlias, str):
            is_valid = False
            errors.append(f"MethodAlias {self.MethodAlias} must have type str.")
        if not property_format.is_weather_method(self.MethodAlias):
            is_valid = False
            errors.append(
                f"MethodAlias {self.MethodAlias} must have format WeatherMethod."
            )
        return is_valid, errors


class Csv_Weather_Tmy_Temp_1_0_0:
    mp_alias = "csv.weather.tmy.temp.1_0_0"

    @classmethod
    def payload_is_valid(
        cls, payload_as_dict: Dict[str, Any]
    ) -> Tuple[bool, Optional[List[str]]]:
        if "WorldInstanceAlias" not in payload_as_dict.keys():
            payload_as_dict["WorldInstanceAlias"] = None

        try:
            p = Payload(
                MpAlias=payload_as_dict["MpAlias"],
                LocationAlias=payload_as_dict["LocationAlias"],
                SourceAlias=payload_as_dict["SourceAlias"],
                MethodAlias=payload_as_dict["MethodAlias"],
                Comment=payload_as_dict["Comment"],
                TimezoneString=payload_as_dict["TimezoneString"],
                TempUnit=payload_as_dict["TempUnit"],
                CreatedAtUnixS=payload_as_dict["CreatedAtUnixS"],
                WeatherUid=payload_as_dict["WeatherUid"],
                MessageId=payload_as_dict["MessageId"],
                Temperatures=payload_as_dict["Temperatures"],
                WorldInstanceAlias=payload_as_dict["WorldInstanceAlias"],
            )
        except TypeError:
            errors = [TypeError]
            return False, errors
        return p.is_valid()

    def __init__(self, weather_csv, world_instance_alias=None):
        self.errors = []
        self.payload = None
        first_data_row = 10
        temperatures = []
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
                    if mp_alias != "csv.weather.tmy.temp.1_0_0":
                        raise Exception(
                            f"MpAlias must be csv.weather.tmy.temp.1_0_0. Instead it was {mp_alias}"
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
                    timezone_string = row[1].strip()
                    if property != "TimezoneString":
                        raise Exception(
                            f"Csv 5,0 must be TimezoneString, instead it is {property}"
                        )
                if line_idx == 6:
                    property = row[0]
                    temp_unit = row[1].strip()
                    if temp_unit == "":
                        temp_unit = None
                    if property != "TempUnit":
                        raise Exception(
                            f"Csv 6,0 must be TempUnit, instead it is {property}"
                        )
                if line_idx == 7:
                    property = row[0]
                    created_at_unix_s = int(row[1].strip())
                    if property != "CreatedAtUnixS":
                        raise Exception(
                            f"Csv 7,0 must be CreatedAtUnixS, instead it is {property}"
                        )
                if line_idx == 8:
                    property = row[0]
                    weather_uid = row[1].strip()
                    if property != "WeatherUid":
                        raise Exception(
                            f"Csv 8,0 must be WeatherUid, instead it is {property}"
                        )
                if line_idx == 9:
                    property = row[0]
                    if property != "Temperatures":
                        raise Exception(
                            f"Csv 9,0 must be Temperatures, instead it is {property}"
                        )
                elif line_idx >= first_data_row:
                    try:
                        temperatures.append(int(row[0]))
                    except ValueError:
                        raise Exception(f"Missing a temperature in row {line_idx+1}")
                line_idx += 1

        p = Payload(
            LocationAlias=location_alias,
            SourceAlias=source_alias,
            MethodAlias=method_alias,
            Comment=comment,
            TimezoneString=timezone_string,
            TempUnit=temp_unit,
            CreatedAtUnixS=created_at_unix_s,
            WeatherUid=weather_uid,
            MessageId=str(uuid.uuid4()),
            Temperatures=temperatures,
            WorldInstanceAlias=world_instance_alias,
        )

        is_valid, errors = p.is_valid()
        if is_valid is False:
            self.errors = errors
            print(errors)
            raise SchemaError(
                f"Failed to create payload due to these errors:{errors}. Input file is {weather_csv}"
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
            SourceAlias=self.payload.SourceAlias,
            MethodAlias=self.payload.MethodAlias,
            Comment=self.payload.Comment,
            TimezoneString=self.payload.TimezoneString,
            TempUnit=self.payload.TempUnit,
            CreatedAtUnixS=self.payload.CreatedAtUnixS,
            WeatherUid=self.payload.WeatherUid,
            Temperatures=self.payload.Temperatures,
            WorldInstanceAlias=world_instance_alias,
            MessageId=str(uuid.uuid4()),
            IrlTimeUtc=log_style_utc_date_w_millis(time.time()),
        )
        return p
