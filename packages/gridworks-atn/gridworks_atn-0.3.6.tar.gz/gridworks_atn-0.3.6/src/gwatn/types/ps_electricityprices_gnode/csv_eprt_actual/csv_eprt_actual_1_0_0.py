import csv
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Tuple

import numpy as np
from gridworks.errors import SchemaError

import gwatn.types.hack_property_format as property_format
from gwatn.types.eprt.gt_eprt_actual_1_0_0 import Gt_Eprt_Actual_1_0_0
from gwatn.types.eprt.gt_eprt_actual_1_0_0 import GtEprtActual100


class Payload(NamedTuple):
    WorldInstanceAlias: str
    Core: GtEprtActual100
    MpAlias: str = "csv.eprt.actual.1_0_0"

    def asdict(self):
        d = self._asdict()
        d["Core"] = self.Core.asdict()
        return d

    def is_valid(self) -> Tuple[bool, Optional[List[str]]]:
        is_valid, errors = self.passes_derived_validations()
        return is_valid, errors

    def passes_derived_validations(self) -> Tuple[bool, Optional[List[str]]]:
        is_valid = True
        errors = []
        if self.MpAlias != "csv.eprt.actual.1_0_0":
            is_valid = False
            errors.append(
                f"Payload requires MpAlias of 'csv.eprt.actual.1_0_0', not {self.MpAlias}."
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
        if not isinstance(self.Core, GtEprtActual100):
            is_valid = False
            errors.append(f"Core {self.Core} must have type GtEprtActual100.")
            raise Exception("Core must have type GtEprtActual100")
        core_is_valid, core_errors = self.Core.is_valid()
        if not core_is_valid:
            is_valid = False
            errors += core_errors
        return is_valid, errors


class Csv_Eprt_Actual_1_0_0:
    def __init__(self, price_file: str, world_instance_alias: str = "dw1__1"):
        file = price_file
        self.errors = []
        self.payload = None
        first_data_row = 9
        prices = np.array([])
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
                    first_market_slot_start_iso8601_utc = row[1].strip()
                    if property != "FirstMarketSlotStartIso8601Utc":
                        raise Exception(
                            f"Csv 4,0 must be FirstMarketSlotStartIso8601Utc, instead it is {property}"
                        )
                if line_idx == 5:
                    property = row[0]
                    try:
                        market_slot_duration_minutes = int(row[1])
                    except:
                        raise Exception(f"MarketSlotDurationMinutes must be an int")
                    if property != "MarketSlotDurationMinutes":
                        raise Exception(
                            f"Csv 5,0 must be MarketSlotDurationMinutes, instead it is {property}"
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
                    header = row[1].strip()
                    if property != "Header":
                        raise Exception(
                            f"Csv 8,0 must be Header, instead it is {property}"
                        )
                    if header != "Real Time LMP Electricity Price (CurrencyUnit/MWh)":
                        raise Exception(
                            f"Csv 8,1 must be 'Real Time LMP Electricity Price (CurrencyUnit/MWh)', instead it is {header}"
                        )
                elif line_idx >= first_data_row:
                    try:
                        prices = np.append(prices, float(row[0]))
                    except:
                        raise Exception(
                            f"Missing a price(or non number) in row {line_idx+1}"
                        )
                line_idx += 1
        try:
            core = Gt_Eprt_Actual_1_0_0(
                method_alias=method_alias,
                prices=list(prices),
                p_node_alias=p_node_alias,
                timezone_string=timezone_string,
                currency_unit=currency_unit,
                market_slot_duration_minutes=market_slot_duration_minutes,
                first_market_slot_start_iso8601_utc=first_market_slot_start_iso8601_utc,
                comment=comment,
            ).payload
        except Exception as e:
            is_valid = (False,)
            raise SchemaError(
                "Failed to create payload due to these errors:{e}. Input file is {price_file}"
            )

        p = Payload(WorldInstanceAlias=world_instance_alias, Core=core)

        is_valid, errors = p.is_valid()
        if is_valid is False:
            self.errors = errors
            print(errors)
            raise SchemaError(
                f"Failed to create payload due to these errors:{errors}. Input file is {price_file}"
            )
        else:
            self.payload = p
