import csv
import datetime
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
from gwatn.types.hack_test_dummy import TEST_DUMMY_AGENT
from gwatn.types.hack_utils import camel_to_snake
from gwatn.types.hack_utils import log_style_utc_date_w_millis
from gwatn.types.hack_utils import snake_to_camel
from gwatn.types.ps_electricityprices_gnode.r_eprt_forecast.r_eprt_forecast_1_0_0 import (
    Payload as REprtForecast100Payload,
)
from gwatn.types.ps_electricityprices_gnode.r_eprt_forecast.r_eprt_forecast_1_0_0 import (
    R_Eprt_Forecast_1_0_0,
)


class Payload(NamedTuple):
    MpAlias: str
    WorldInstanceAlias: str
    PNodeAlias: str
    MethodAlias: str
    Comment: str
    ForecastGeneratedIso8601Utc: str
    ForecastStartIso8601Utc: str
    TimezoneString: str
    CurrencyUnit: str
    PriceUid: str
    Header: str
    Prices: list
    SliceDurationMinutesList: List[int]

    def asdict(self):
        d = self._asdict()
        return d

    def is_valid(self) -> Tuple[bool, Optional[List[str]]]:
        is_valid, errors = self.passes_derived_validations()
        return is_valid, errors

    def passes_derived_validations(self) -> Tuple[bool, Optional[List[str]]]:
        is_valid = True
        errors = []
        if self.MpAlias != "csv.eprt.forecast.1_0_0":
            is_valid = False
            errors.append(
                f"Payload requires MpAlias of 'csv.eprt.forecast.1_0_0', not {self.MpAlias}."
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
        if not isinstance(self.PNodeAlias, str):
            is_valid = False
            errors.append(f"PNodeAlias must have type str.")
        if not property_format.is_recognized_p_node_alias(self.PNodeAlias):
            is_valid = False
            errors.append(
                f"PNodeAlias {self.PNodeAlias} must have format RecognizedPNodeAlias."
            )
        if not isinstance(self.ForecastGeneratedIso8601Utc, str):
            is_valid = False
            errors.append("ForecastGeneratedIso8601Utc must have type str")
        if not property_format.is_recognized_iso8601_utc(
            self.ForecastGeneratedIso8601Utc
        ):
            is_valid = False
            errors.append(f"ForecastGeneratedIso8601Utc must have format Iso8601.")
        if not isinstance(self.ForecastStartIso8601Utc, str):
            is_valid = False
            errors.append("ForecastStartIso8601Utc must have type str")
        if not property_format.is_recognized_iso8601_utc(self.ForecastStartIso8601Utc):
            is_valid = False
            errors.append(f"ForecastStartIso8601Utc must have format Iso8601.")
        if not isinstance(self.SliceDurationMinutesList, list):
            is_valid = False
            errors.append(f"SliceDurationMinutesList must have type list.")
        else:
            for elt in self.SliceDurationMinutesList:
                if not isinstance(elt, int):
                    is_valid = False
                    errors.append(
                        f"elements of SliceDurationMinutesList must have type int"
                    )
        if not isinstance(self.TimezoneString, str):
            is_valid = False
            errors.append(f"TimezoneString {self.TimezoneString} must have type str.")
        if not property_format.is_recognized_timezone_string(self.TimezoneString):
            is_valid = False
            errors.append(
                f"TimezoneString must be a recognized timezone (pytz.timezone)"
            )
        if not isinstance(self.CurrencyUnit, str):
            is_valid = False
            errors.append(f"CurrencyUnit {self.CurrencyUnit} must have type str.")
        if not property_format.is_recognized_currency_unit(self.CurrencyUnit):
            is_valid = False
            errors.append(
                f"CurrencyUnit {self.CurrencyUnit} must have format RecognizedCurrencyUnit."
            )
        if not isinstance(self.PriceUid, str):
            is_valid = False
            errors.append(f"PriceUid {self.PriceUid} must have type str.")
        if not property_format.is_uuid_canonical_textual(self.PriceUid):
            is_valid = False
            errors.append(
                f"PriceUid {self.PriceUid} must have format UuidCanonicalTextual."
            )

        return is_valid, errors


class Csv_Eprt_Forecast_1_0_0:
    mp_alias = "csv.eprt.forecast.1_0_0"

    @classmethod
    def payload_is_valid(
        cls, payload_as_dict: Dict[str, Any]
    ) -> Tuple[bool, Optional[List[str]]]:
        try:
            p = Payload(
                MpAlias=payload_as_dict["MpAlias"],
                WorldInstanceAlias=payload_as_dict["WorldInstanceAlias"],
                PNodeAlias=payload_as_dict["PNodeAlias"],
                MethodAlias=payload_as_dict["MethodAlias"],
                Comment=payload_as_dict["Comment"],
                ForecastGeneratedIso8601Utc=payload_as_dict[
                    "ForecastGeneratedIso8601Utc"
                ],
                ForecastStartIso8601Utc=payload_as_dict["ForecastStartIso8601Utc"],
                SliceDurationMinutesList=payload_as_dict["SliceDurationMinutesList"],
                TimezoneString=payload_as_dict["TimezoneString"],
                CurrencyUnit=payload_as_dict["CurrencyUnit"],
                PriceUid=payload_as_dict["PriceUid"],
                Header=payload_as_dict["Header"],
                Prices=payload_as_dict["Prices"],
            )
        except TypeError:
            errors = [TypeError]
            return False, errors
        return p.is_valid()

    def __init__(self, real_time_electricity_price_csv):
        file = real_time_electricity_price_csv
        self.errors = []
        self.payload = None
        first_data_row = 10
        prices = np.array([])
        slice_duration_minutes_list = np.array([])
        with open(real_time_electricity_price_csv, newline="") as csvfile:
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
                    p_node_alias = row[1].strip()
                    if property != "PNodeAlias":
                        raise Exception(
                            f"Csv 1,0 must be PNodeAlias, instead it is {property}"
                        )
                if line_idx == 2:
                    property = row[0]
                    method_alias = row[1].strip()
                    if property != "MethodAlias":
                        raise Exception(
                            f"Csv 2,0 must be MethodAlias, instead it is {property}. Check file {file}."
                        )
                if line_idx == 3:
                    property = row[0]
                    comment = row[1].strip()
                    if property != "Comment":
                        raise Exception(
                            f"Csv 3,0 must be Comment, instead it is {property}"
                        )
                if line_idx == 4:
                    property = row[0]
                    forecast_generated_iso8601_utc = row[1].strip()
                    if property != "ForecastGeneratedIso8601Utc":
                        raise Exception(
                            f"Csv 4,0 must be ForecastGeneratedIso8601Utc, instead it is {property}"
                        )
                if line_idx == 5:
                    property = row[0]
                    forecast_start_iso8601_utc = row[1].strip()
                    if property != "ForecastStartIso8601Utc":
                        raise Exception(
                            f"Csv 5,0 must be ForecastStartIso8601Utc, instead it is {property}"
                        )
                if line_idx == 6:
                    property = row[0]
                    timezone_string = row[1].strip()
                    if property != "TimezoneString":
                        raise Exception(
                            f"Csv 6,0 must be TimezoneString, instead it is {property}"
                        )
                if line_idx == 7:
                    property = row[0]
                    currency_unit = row[1].strip()
                    if property != "CurrencyUnit":
                        raise Exception(
                            f"Csv 7,0 must be CurrencyUnit, instead it is {property}"
                        )
                if line_idx == 8:
                    property = row[0]
                    price_uid = row[1].strip()
                    if property != "PriceUid":
                        raise Exception(
                            f"Csv 8,0 must be PriceUid, instead it is {property}"
                        )
                if line_idx == 9:
                    property = row[0]
                    header = row[1].strip()
                    if property != "Header":
                        raise Exception(
                            f"Csv 9,0 must be Header, instead it is {property}"
                        )
                    if (
                        header
                        != "Forecast Real Time LMP Electricity Price (Currency Unit/MWh), Forecast Period in Minutes"
                    ):
                        raise Exception(
                            f"Csv 9,1 must be 'Forecast Real Time LMP Electricity Price (Currency Unit/MWh), Forecast Period in Minutes', instead it is {header}"
                        )
                elif line_idx >= first_data_row:
                    try:
                        prices = np.append(prices, float(row[0]))
                        slice_duration_minutes_list = np.append(
                            slice_duration_minutes_list, int(row[1])
                        )
                    except:
                        raise Exception(
                            f"Missing a price(or non number) in row {line_idx+1}"
                        )
                line_idx += 1

        p = Payload(
            MpAlias=mp_alias,
            WorldInstanceAlias="dw1__1",
            PNodeAlias=p_node_alias,
            MethodAlias=method_alias,
            Comment=comment,
            ForecastGeneratedIso8601Utc=forecast_generated_iso8601_utc,
            ForecastStartIso8601Utc=forecast_start_iso8601_utc,
            SliceDurationMinutesList=slice_duration_minutes_list,
            TimezoneString=timezone_string,
            CurrencyUnit=currency_unit,
            PriceUid=price_uid,
            Header=header,
            Prices=list(prices),
        )

        is_valid, errors = p.is_valid()
        if is_valid is False:
            self.errors = errors
            print(errors)
            raise SchemaError(
                f"Failed to create payload due to these errors: {errors}. Input file is {real_time_electricity_price_csv}"
            )
        else:
            self.payload = p

    def paired_rabbit_payload(self, agent=TEST_DUMMY_AGENT) -> REprtForecast100Payload:
        return R_Eprt_Forecast_1_0_0(
            agent=agent,
            prices=self.payload.Prices,
            time_slice_duration_minutes_list=self.payload.SliceDurationMinutesList,
            method_alias=self.payload.MethodAlias,
            forecast_generated_iso8601_utc=self.payload.ForecastGeneratedIso8601Utc,
            forecast_start_iso8601_utc=self.payload.ForecastStartIso8601Utc,
            currency_unit=self.payload.CurrencyUnit,
            p_node_alias=self.payload.PNodeAlias,
            price_uid=self.payload.PriceUid,
            timezone_string=self.payload.TimezoneString,
            comment=self.payload.Comment,
        ).payload
