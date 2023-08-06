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
from gwatn.types.hack_type_base import HackTypeBase
from gwatn.types.hack_utils import log_style_utc_date_w_millis
from gwatn.types.ws_irradiances_gnode.r_irradiance_poa_template.r_irradiance_poa_template_1_0_0 import (
    Payload as PairedRabbitPayload,
)


class Payload(NamedTuple):
    LocationAlias: str
    SourceAlias: str
    MethodAlias: str
    Comment: str
    TimezoneString: str
    WeatherUid: str
    IrradiancePoaWPerM2: list
    MessageId: str
    WorldInstanceAlias: Optional[str] = None
    MpAlias: str = "csv.irradiance.poa.template.1_0_0"

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
        if self.MpAlias != "csv.irradiance.poa.template.1_0_0":
            is_valid = False
            errors.append(
                f"Payload requires MpAlias of 'csv.irradiance.poa.template.1_0_0', not {self.MpAlias}."
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
        if not isinstance(self.IrradiancePoaWPerM2, list):
            is_valid = False
            errors.append(f"IrradiancePoaWPerM2 must have type list")
        if not property_format.is_valid_month_hour_int_array(self.IrradiancePoaWPerM2):
            errors.append(
                f"IrradiancePoaWPerM2 must have format ValidMonthHourIntArray: a list of 12 months, where each month is a list of 24 ints."
            )
        if not isinstance(self.MessageId, str):
            is_valid = False
            errors.append(f"MessageId {self.MessageId} must have type str.")
        if not property_format.is_uuid_canonical_textual(self.MessageId):
            is_valid = False
            errors.append(
                f"MessageId {self.MessageId} must have format UuidCanonicalTextual."
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


class Csv_Irradiance_Poa_Template_1_0_0:
    mp_alias = "csv.irradiance.poa.template.1_0_0"

    @classmethod
    def payload_is_valid(
        cls, payload_as_dict: Dict[str, Any]
    ) -> Tuple[bool, Optional[List[str]]]:
        try:
            p = Payload(
                LocationAlias=payload_as_dict["LocationAlias"],
                SourceAlias=payload_as_dict["SourceAlias"],
                MethodAlias=payload_as_dict["MethodAlias"],
                Comment=payload_as_dict["Comment"],
                TimezoneString=payload_as_dict["TimezoneString"],
                WeatherUid=payload_as_dict["WeatherUid"],
                IrradiancePoaWPerM2=payload_as_dict["IrradiancePoaWPerM2"],
                MessageId=payload_as_dict["MessageId"],
                WorldInstanceAlias=payload_as_dict["WorldInstanceAlias"],
            )
        except TypeError:
            errors = [TypeError]
            return False, errors
        return p.is_valid()

    def __init__(self, irradiance_csv):
        self.errors = []
        self.payload = None
        first_data_row = 9
        irradiance_poa_w_per_m2 = [[], [], [], [], [], [], [], [], [], [], [], []]
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
                    timezone_string = row[1].strip()
                    if property != "TimezoneString":
                        raise Exception(
                            f"Csv 5,0 must be TimezoneString, instead it is {property}"
                        )
                if line_idx == 6:
                    property = row[0]
                    price_uid = row[1].strip()
                    if property != "WeatherUid":
                        raise Exception(
                            f"Csv 6,0 must be WeatherUid, instead it is {property}"
                        )
                if line_idx == 7:
                    property = row[0]
                    header = row[1].strip()
                    if property != "Header":
                        raise Exception(
                            f"Csv 7,0 must be Header, instead it is {property}"
                        )
                    if (
                        header
                        != "Clear Sky Plain of Array Irradiance By Month and Hour (W/M2)"
                    ):
                        raise Exception(
                            f"Csv 7,1 must be 'Clear Sky Plain of Array Irradiance By Month and Hour (W/M2)', instead it is {header}"
                        )
                if line_idx == 8:
                    hour_month = row[0]
                    if hour_month != "Hour/Month":
                        raise Exception(
                            f"Csv 8,0 must be 'Hour/Month', instead it is {property}"
                        )
                    for month_idx in range(1, 13):
                        if month_idx != int(row[month_idx]):
                            raise Exception(
                                f"Csv 8,{month_idx} must be {month_idx} (to reflect month {month_idx}. Instead it was {int(row[month_idx])} "
                            )
                elif line_idx >= first_data_row:
                    hour = line_idx + 1 - first_data_row
                    hour_label = int(row[0])
                    if hour_label != hour:
                        raise Exception(
                            f"Csv {line_idx},0 must be {hour} (to reflect that hour. Instead it was {hour_label} "
                        )
                    for month in range(1, 13):
                        try:
                            irradiance_poa_w_per_m2[month - 1].append(int(row[month]))
                        except ValueError:
                            raise Exception(
                                f"Need an int Irradiance measure in cell {line_idx},{month}. Instead it is {row[month]}"
                            )
                line_idx += 1

        p = Payload(
            LocationAlias=location_alias,
            SourceAlias=source_alias,
            MethodAlias=method_alias,
            Comment=comment,
            TimezoneString=timezone_string,
            WeatherUid=price_uid,
            IrradiancePoaWPerM2=irradiance_poa_w_per_m2,
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
            SourceAlias=self.payload.SourceAlias,
            MethodAlias=self.payload.MethodAlias,
            Comment=self.payload.Comment,
            TimezoneString=self.payload.TimezoneString,
            WeatherUid=self.payload.WeatherUid,
            IrradiancePoaWPerM2=self.payload.IrradiancePoaWPerM2,
            MessageId=str(uuid.uuid4()),
            WorldInstanceAlias=world_instance_alias,
            IrlTimeUtc=log_style_utc_date_w_millis(time.time()),
        )
        return p
