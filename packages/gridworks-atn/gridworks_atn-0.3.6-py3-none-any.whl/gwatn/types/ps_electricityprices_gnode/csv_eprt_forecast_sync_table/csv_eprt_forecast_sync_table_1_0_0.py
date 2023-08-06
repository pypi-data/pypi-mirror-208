import csv
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Tuple

import numpy as np
import pendulum
from gridworks.errors import SchemaError

import gwatn.types.hack_property_format as property_format
from gwatn.types.eprt.gt_eprt_forecast_sync_1_0_0 import Gt_Eprt_Forecast_Sync_1_0_0
from gwatn.types.eprt.gt_eprt_forecast_sync_1_0_0 import GtEprtForecastSync100
from gwatn.types.hack_test_dummy import TEST_DUMMY_AGENT


class Payload(NamedTuple):
    CoreList: List[GtEprtForecastSync100]
    WorldInstanceAlias: str
    MpAlias: str = "csv.eprt.forecast.sync.table.1_0_0"

    def asdict(self):
        d = self._asdict()
        d["CoreList"] = []
        for elt in self.CoreList:
            d["CoreList"].append(elt.asdict())
        return d

    def is_valid(self) -> Tuple[bool, Optional[List[str]]]:
        is_valid, errors = self.passes_derived_validations()
        return is_valid, errors

    def passes_derived_validations(self) -> Tuple[bool, Optional[List[str]]]:
        is_valid = True
        errors = []
        if self.MpAlias != "csv.eprt.forecast.sync.table.1_0_0":
            is_valid = False
            errors.append(
                f"Payload requires MpAlias of 'csv.eprt.forecast.sync.table.1_0_0', not {self.MpAlias}."
            )
        if not isinstance(self.WorldInstanceAlias, str):
            is_valid = False
            errors.append(
                f"WorldInstanceAlias {self.WorldInstanceAlias} must have type str."
            )
        if not isinstance(self.CoreList, list):
            is_valid = False
            errors.append(f"CoreList {self.CoreList} must have type list")
        for elt in self.CoreList:
            if not isinstance(elt, GtEprtForecastSync100):
                is_valid = False
                errors.append(f"Core {elt} must have type GtEprtForecastSync100.")
            core_is_valid, core_errors = elt.is_valid()
            if not core_is_valid:
                is_valid = False
                errors.append(core_errors)
        return is_valid, errors


class Csv_Eprt_Forecast_Sync_Table_1_0_0:
    def __init__(self, price_file: str, world_instance_alias: str = "dw1__1"):
        file = price_file
        self.errors = []
        self.payload = None
        first_data_row = 10
        with open(price_file, newline="") as csvfile:
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
                    if mp_alias != "csv.eprt.forecast.sync.table.1_0_0":
                        raise Exception(
                            f"Csv 0,1 must be csv.eprt.forecast.sync.table.1_0_0, instead it is {mp_alias} (file {price_file}):"
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
                            f"Csv 2,0 must be MethodAlias, instead it is {property}.  (file {file})"
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
                    try:
                        generated_prior_to_start_minutes = int(row[1])
                    except ValueError as e:
                        raise Exception(
                            f"GeneratedPriorToStartMinutes {row[1]} must be int! (file {file})"
                        )
                    if property != "GeneratedPriorToStartMinutes":
                        raise Exception(
                            f"Csv 4,0 must be GeneratedPriorToStartMinutes, instead it is {property}"
                        )
                if line_idx == 5:
                    property = row[0]
                    first_forecast_start_iso8601_utc = row[1].strip()
                    if property != "FirstForecastStartIso8601Utc":
                        raise Exception(
                            f"Csv 5,0 must be FirstForecastStartIso8601Utc, instead it is {property}"
                        )
                if line_idx == 6:
                    property = row[0]
                    try:
                        uniform_slice_duration_minutes = int(row[1])
                    except:
                        raise Exception(
                            f"UniformSliceDurationMinutes {row[1]}  must be int! (file {file})"
                        )
                    if property != "UniformSliceDurationMinutes":
                        raise Exception(
                            f"Csv 6,0 must be UniformSliceDurationMinutes, instead it is {property}"
                        )
                if line_idx == 7:
                    property = row[0]
                    timezone_string = row[1].strip()
                    if property != "TimezoneString":
                        raise Exception(
                            f"Csv 7,0 must be TimezoneString, instead it is {property}"
                        )
                if line_idx == 8:
                    property = row[0]
                    currency_unit = row[1].strip()
                    if property != "CurrencyUnit":
                        raise Exception(
                            f"Csv 8,0 must be CurrencyUnit, instead it is {property}"
                        )
                if line_idx == 9:
                    property = row[0]
                    first_price_uid = row[1].strip()
                    if not property_format.is_uuid_canonical_textual(first_price_uid):
                        raise Exception(
                            f"Csv 1,0 SubmessagePriceUid must pass property_format.is_uuid_canonical_textual (file {file})"
                        )
                    price_uids = [first_price_uid]
                    grabbing_valid_columns = True
                    while grabbing_valid_columns:
                        try:
                            new_price_uid = row[len(price_uids) + 1].strip()
                        except:
                            grabbing_valid_columns = False
                        if grabbing_valid_columns:
                            if not property_format.is_uuid_canonical_textual(
                                new_price_uid
                            ):
                                grabbing_valid_columns = False
                            else:
                                price_uids.append(new_price_uid)
                    total_forecasts = len(price_uids)
                    prices = [np.array([]) for i in range(total_forecasts)]
                    if property != "SubMessagePriceUid":
                        raise Exception(
                            f"Csv 9,0 must be SubMessagePriceUid, instead it is {property}"
                        )
                elif line_idx >= first_data_row:
                    for col_idx in range(total_forecasts):
                        try:
                            prices[col_idx] = np.append(
                                prices[col_idx], float(row[col_idx + 1])
                            )
                        except:
                            raise Exception(
                                f"Missing a price(or non number) in col {col_idx + 2}, row {line_idx+1} (file {file})"
                            )
                line_idx += 1
        core_start_iso8601_utc_list = []
        core_list = []
        for forecast_idx in range(total_forecasts):
            new_core_start_utc = pendulum.parse(
                first_forecast_start_iso8601_utc
            ) + pendulum.duration(minutes=forecast_idx * uniform_slice_duration_minutes)
            new_core_start_iso8601_utc = new_core_start_utc.to_iso8601_string()
            new_core_generated_utc = new_core_start_utc - pendulum.duration(
                minutes=generated_prior_to_start_minutes
            )
            new_core_generated_iso8601_utc = new_core_generated_utc.to_iso8601_string()
            core_start_iso8601_utc_list.append(new_core_start_iso8601_utc)
            try:
                new_core = Gt_Eprt_Forecast_Sync_1_0_0(
                    method_alias=method_alias,
                    prices=list(prices[forecast_idx]),
                    p_node_alias=p_node_alias,
                    timezone_string=timezone_string,
                    currency_unit=currency_unit,
                    uniform_slice_duration_minutes=uniform_slice_duration_minutes,
                    forecast_generated_iso8601_utc=new_core_generated_iso8601_utc,
                    forecast_start_iso8601_utc=new_core_start_iso8601_utc,
                    price_uid=price_uids[forecast_idx],
                    comment=comment,
                ).payload
            except Exception as e:
                raise Exception(
                    f"Error in column {forecast_idx + 2} of {price_file}: {e}"
                )
            core_list.append(new_core)

        p = Payload(WorldInstanceAlias=world_instance_alias, CoreList=core_list)

        is_valid, errors = p.is_valid()
        if is_valid is False:
            self.errors = errors
            print(errors)
            raise SchemaError(
                f"Failed to create payload due to these errors:{errors}. Input file is {price_file}"
            )
        else:
            self.payload = p
