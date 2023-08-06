"""Type flo.params.brickstorageheater, version 000"""
import json
from enum import auto
from typing import Any
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional

from fastapi_utils.enums import StrEnum
from gridworks.errors import SchemaError
from gridworks.message import as_enum
from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from gwatn.enums import RecognizedCurrencyUnit
from gwatn.enums import RecognizedTemperatureUnit


class RecognizedCurrencyUnit000SchemaEnum:
    enum_name: str = "recognized.currency.unit.000"
    symbols: List[str] = [
        "00000000",
        "e57c5143",
        "f7b38fc5",
    ]

    @classmethod
    def is_symbol(cls, candidate: str) -> bool:
        if candidate in cls.symbols:
            return True
        return False


class RecognizedCurrencyUnit000(StrEnum):
    UNKNOWN = auto()
    USD = auto()
    GBP = auto()

    @classmethod
    def default(cls) -> "RecognizedCurrencyUnit000":
        return cls.UNKNOWN

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]


class RecognizedCurrencyUnitMap:
    @classmethod
    def type_to_local(cls, symbol: str) -> RecognizedCurrencyUnit:
        if not RecognizedCurrencyUnit000SchemaEnum.is_symbol(symbol):
            raise SchemaError(
                f"{symbol} must belong to RecognizedCurrencyUnit000 symbols"
            )
        versioned_enum = cls.type_to_versioned_enum_dict[symbol]
        return as_enum(
            versioned_enum, RecognizedCurrencyUnit, RecognizedCurrencyUnit.default()
        )

    @classmethod
    def local_to_type(cls, recognized_currency_unit: RecognizedCurrencyUnit) -> str:
        if not isinstance(recognized_currency_unit, RecognizedCurrencyUnit):
            raise SchemaError(
                f"{recognized_currency_unit} must be of type {RecognizedCurrencyUnit}"
            )
        versioned_enum = as_enum(
            recognized_currency_unit,
            RecognizedCurrencyUnit000,
            RecognizedCurrencyUnit000.default(),
        )
        return cls.versioned_enum_to_type_dict[versioned_enum]

    type_to_versioned_enum_dict: Dict[str, RecognizedCurrencyUnit000] = {
        "00000000": RecognizedCurrencyUnit000.UNKNOWN,
        "e57c5143": RecognizedCurrencyUnit000.USD,
        "f7b38fc5": RecognizedCurrencyUnit000.GBP,
    }

    versioned_enum_to_type_dict: Dict[RecognizedCurrencyUnit000, str] = {
        RecognizedCurrencyUnit000.UNKNOWN: "00000000",
        RecognizedCurrencyUnit000.USD: "e57c5143",
        RecognizedCurrencyUnit000.GBP: "f7b38fc5",
    }


class RecognizedTemperatureUnit000SchemaEnum:
    enum_name: str = "recognized.temperature.unit.000"
    symbols: List[str] = [
        "00000000",
        "6f16ee63",
    ]

    @classmethod
    def is_symbol(cls, candidate: str) -> bool:
        if candidate in cls.symbols:
            return True
        return False


class RecognizedTemperatureUnit000(StrEnum):
    C = auto()
    F = auto()

    @classmethod
    def default(cls) -> "RecognizedTemperatureUnit000":
        return cls.C

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]


class RecognizedTemperatureUnitMap:
    @classmethod
    def type_to_local(cls, symbol: str) -> RecognizedTemperatureUnit:
        if not RecognizedTemperatureUnit000SchemaEnum.is_symbol(symbol):
            raise SchemaError(
                f"{symbol} must belong to RecognizedTemperatureUnit000 symbols"
            )
        versioned_enum = cls.type_to_versioned_enum_dict[symbol]
        return as_enum(
            versioned_enum,
            RecognizedTemperatureUnit,
            RecognizedTemperatureUnit.default(),
        )

    @classmethod
    def local_to_type(
        cls, recognized_temperature_unit: RecognizedTemperatureUnit
    ) -> str:
        if not isinstance(recognized_temperature_unit, RecognizedTemperatureUnit):
            raise SchemaError(
                f"{recognized_temperature_unit} must be of type {RecognizedTemperatureUnit}"
            )
        versioned_enum = as_enum(
            recognized_temperature_unit,
            RecognizedTemperatureUnit000,
            RecognizedTemperatureUnit000.default(),
        )
        return cls.versioned_enum_to_type_dict[versioned_enum]

    type_to_versioned_enum_dict: Dict[str, RecognizedTemperatureUnit000] = {
        "00000000": RecognizedTemperatureUnit000.C,
        "6f16ee63": RecognizedTemperatureUnit000.F,
    }

    versioned_enum_to_type_dict: Dict[RecognizedTemperatureUnit000, str] = {
        RecognizedTemperatureUnit000.C: "00000000",
        RecognizedTemperatureUnit000.F: "6f16ee63",
    }


def check_is_uuid_canonical_textual(v: str) -> None:
    """
    UuidCanonicalTextual format:  A string of hex words separated by hyphens
    of length 8-4-4-4-12.

    Raises:
        ValueError: if not UuidCanonicalTextual format
    """
    try:
        x = v.split("-")
    except AttributeError as e:
        raise ValueError(f"Failed to split on -: {e}")
    if len(x) != 5:
        raise ValueError(f"{v} split by '-' did not have 5 words")
    for hex_word in x:
        try:
            int(hex_word, 16)
        except ValueError:
            raise ValueError(f"Words of {v} are not all hex")
    if len(x[0]) != 8:
        raise ValueError(f"{v} word lengths not 8-4-4-4-12")
    if len(x[1]) != 4:
        raise ValueError(f"{v} word lengths not 8-4-4-4-12")
    if len(x[2]) != 4:
        raise ValueError(f"{v} word lengths not 8-4-4-4-12")
    if len(x[3]) != 4:
        raise ValueError(f"{v} word lengths not 8-4-4-4-12")
    if len(x[4]) != 12:
        raise ValueError(f"{v} word lengths not 8-4-4-4-12")


def check_is_left_right_dot(v: str) -> None:
    """
    LeftRightDot format: Lowercase alphanumeric words separated by periods,
    most significant word (on the left) starting with an alphabet character.

    Raises:
        ValueError: if not LeftRightDot format
    """
    from typing import List

    try:
        x: List[str] = v.split(".")
    except:
        raise ValueError(f"Failed to seperate {v} into words with split'.'")
    first_word = x[0]
    first_char = first_word[0]
    if not first_char.isalpha():
        raise ValueError(f"Most significant word of {v} must start with alphabet char.")
    for word in x:
        if not word.isalnum():
            raise ValueError(f"words of {v} split by by '.' must be alphanumeric.")
    if not v.islower():
        raise ValueError(f"All characters of {v} must be lowercase.")


class FloParamsBrickstorageheater(BaseModel):
    """.

    FloParams for the BrickStorageHeater AtomicTNode strategy.
    [More info](https://gridworks-atn.readthedocs.io/en/latest/brick-storage-heater.html).
    """

    MaxBrickTempC: int = Field(
        title="MaxBrickTempC",
        default=190,
    )
    RatedMaxPowerKw: float = Field(
        title="RatedMaxPowerKw",
        default=13.5,
    )
    ROff: float = Field(
        title="ROff",
        default=0.08,
    )
    ROn: float = Field(
        title="ROn",
        default=0.15,
    )
    RoomTempF: int = Field(
        title="RoomTempF",
        default=70,
    )
    CurrencyUnit: RecognizedCurrencyUnit = Field(
        title="CurrencyUnit",
        default=RecognizedCurrencyUnit.USD,
    )
    TempUnit: RecognizedTemperatureUnit = Field(
        title="TempUnit",
        default=RecognizedTemperatureUnit.F,
    )
    TimezoneString: str = Field(
        title="TimezoneString",
        default="US/Eastern",
    )
    HomeCity: str = Field(
        title="HomeCity",
        default="MILLINOCKET_ME",
    )
    IsRegulating: bool = Field(
        title="IsRegulating",
        default=False,
    )
    StorageSteps: int = Field(
        title="StorageSteps",
        default=100,
    )
    SliceDurationMinutes: List[int] = Field(
        title="SliceDurationMinutes",
        default=[60],
    )
    PowerRequiredByHouseFromSystemAvgKwList: List[float] = Field(
        title="PowerRequiredByHouseFromSystemAvgKwList",
        default=[3.42],
    )
    C: Optional[float] = Field(
        title="C",
        default=200,
    )
    RealtimeElectricityPrice: List[float] = Field(
        title="RealtimeElectricityPrice",
        default=[10.35],
    )
    OutsideTempF: List[float] = Field(
        title="OutsideTempF",
        default=[-5.1],
    )
    DistributionPrice: List[float] = Field(
        title="DistributionPrice",
        default=[40.0],
    )
    RtElecPriceUid: str = Field(
        title="RtElecPriceUid",
    )
    RegulationPrice: List[float] = Field(
        title="RegulationPrice",
        default=[25.3],
    )
    WeatherUid: str = Field(
        title="WeatherUid",
    )
    DistPriceUid: Optional[str] = Field(
        title="DistPriceUid",
        default=None,
    )
    RegPriceUid: Optional[str] = Field(
        title="RegPriceUid",
        default=None,
    )
    StartYearUtc: int = Field(
        title="StartYearUtc",
        default=2020,
    )
    StartMonthUtc: int = Field(
        title="StartMonthUtc",
        default=1,
    )
    StartDayUtc: int = Field(
        title="StartDayUtc",
        default=1,
    )
    StartHourUtc: int = Field(
        title="StartHourUtc",
        default=0,
    )
    StartMinuteUtc: int = Field(
        title="StartMinuteUtc",
        default=0,
    )
    StartingStoreIdx: int = Field(
        title="StartingStoreIdx",
        default=50,
    )
    AmbientPowerInKw: float = Field(
        title="AmbientPowerInKw",
        default=1.25,
    )
    HouseWorstCaseTempF: int = Field(
        title="HouseWorstCaseTempF",
        default=-7,
    )
    GNodeAlias: str = Field(
        title="GNodeAlias",
    )
    FloParamsUid: str = Field(
        title="FloParamsUid",
    )
    TypeName: Literal["flo.params.brickstorageheater"] = "flo.params.brickstorageheater"
    Version: str = "000"

    @validator("CurrencyUnit")
    def _check_currency_unit(cls, v: RecognizedCurrencyUnit) -> RecognizedCurrencyUnit:
        return as_enum(v, RecognizedCurrencyUnit, RecognizedCurrencyUnit.UNKNOWN)

    @validator("TempUnit")
    def _check_temp_unit(
        cls, v: RecognizedTemperatureUnit
    ) -> RecognizedTemperatureUnit:
        return as_enum(v, RecognizedTemperatureUnit, RecognizedTemperatureUnit.C)

    @validator("RtElecPriceUid")
    def _check_rt_elec_price_uid(cls, v: str) -> str:
        try:
            check_is_uuid_canonical_textual(v)
        except ValueError as e:
            raise ValueError(
                f"RtElecPriceUid failed UuidCanonicalTextual format validation: {e}"
            )
        return v

    @validator("WeatherUid")
    def _check_weather_uid(cls, v: str) -> str:
        try:
            check_is_uuid_canonical_textual(v)
        except ValueError as e:
            raise ValueError(
                f"WeatherUid failed UuidCanonicalTextual format validation: {e}"
            )
        return v

    @validator("DistPriceUid")
    def _check_dist_price_uid(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            check_is_uuid_canonical_textual(v)
        except ValueError as e:
            raise ValueError(
                f"DistPriceUid failed UuidCanonicalTextual format validation: {e}"
            )
        return v

    @validator("RegPriceUid")
    def _check_reg_price_uid(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            check_is_uuid_canonical_textual(v)
        except ValueError as e:
            raise ValueError(
                f"RegPriceUid failed UuidCanonicalTextual format validation: {e}"
            )
        return v

    @validator("GNodeAlias")
    def _check_g_node_alias(cls, v: str) -> str:
        try:
            check_is_left_right_dot(v)
        except ValueError as e:
            raise ValueError(f"GNodeAlias failed LeftRightDot format validation: {e}")
        return v

    @validator("FloParamsUid")
    def _check_flo_params_uid(cls, v: str) -> str:
        try:
            check_is_uuid_canonical_textual(v)
        except ValueError as e:
            raise ValueError(
                f"FloParamsUid failed UuidCanonicalTextual format validation: {e}"
            )
        return v

    def as_dict(self) -> Dict[str, Any]:
        d = self.dict()
        del d["CurrencyUnit"]
        CurrencyUnit = as_enum(
            self.CurrencyUnit, RecognizedCurrencyUnit, RecognizedCurrencyUnit.default()
        )
        d["CurrencyUnitGtEnumSymbol"] = RecognizedCurrencyUnitMap.local_to_type(
            CurrencyUnit
        )
        del d["TempUnit"]
        TempUnit = as_enum(
            self.TempUnit,
            RecognizedTemperatureUnit,
            RecognizedTemperatureUnit.default(),
        )
        d["TempUnitGtEnumSymbol"] = RecognizedTemperatureUnitMap.local_to_type(TempUnit)
        if d["C"] is None:
            del d["C"]
        if d["DistPriceUid"] is None:
            del d["DistPriceUid"]
        if d["RegPriceUid"] is None:
            del d["RegPriceUid"]
        return d

    def as_type(self) -> str:
        return json.dumps(self.as_dict())

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class FloParamsBrickstorageheater_Maker:
    type_name = "flo.params.brickstorageheater"
    version = "000"

    def __init__(
        self,
        max_brick_temp_c: int,
        rated_max_power_kw: float,
        r_off: float,
        r_on: float,
        room_temp_f: int,
        currency_unit: RecognizedCurrencyUnit,
        temp_unit: RecognizedTemperatureUnit,
        timezone_string: str,
        home_city: str,
        is_regulating: bool,
        storage_steps: int,
        slice_duration_minutes: List[int],
        power_required_by_house_from_system_avg_kw_list: List[float],
        c: Optional[float],
        realtime_electricity_price: List[float],
        outside_temp_f: List[float],
        distribution_price: List[float],
        rt_elec_price_uid: str,
        regulation_price: List[float],
        weather_uid: str,
        dist_price_uid: Optional[str],
        reg_price_uid: Optional[str],
        start_year_utc: int,
        start_month_utc: int,
        start_day_utc: int,
        start_hour_utc: int,
        start_minute_utc: int,
        starting_store_idx: int,
        ambient_power_in_kw: float,
        house_worst_case_temp_f: int,
        g_node_alias: str,
        flo_params_uid: str,
    ):
        self.tuple = FloParamsBrickstorageheater(
            MaxBrickTempC=max_brick_temp_c,
            RatedMaxPowerKw=rated_max_power_kw,
            ROff=r_off,
            ROn=r_on,
            RoomTempF=room_temp_f,
            CurrencyUnit=currency_unit,
            TempUnit=temp_unit,
            TimezoneString=timezone_string,
            HomeCity=home_city,
            IsRegulating=is_regulating,
            StorageSteps=storage_steps,
            SliceDurationMinutes=slice_duration_minutes,
            PowerRequiredByHouseFromSystemAvgKwList=power_required_by_house_from_system_avg_kw_list,
            C=c,
            RealtimeElectricityPrice=realtime_electricity_price,
            OutsideTempF=outside_temp_f,
            DistributionPrice=distribution_price,
            RtElecPriceUid=rt_elec_price_uid,
            RegulationPrice=regulation_price,
            WeatherUid=weather_uid,
            DistPriceUid=dist_price_uid,
            RegPriceUid=reg_price_uid,
            StartYearUtc=start_year_utc,
            StartMonthUtc=start_month_utc,
            StartDayUtc=start_day_utc,
            StartHourUtc=start_hour_utc,
            StartMinuteUtc=start_minute_utc,
            StartingStoreIdx=starting_store_idx,
            AmbientPowerInKw=ambient_power_in_kw,
            HouseWorstCaseTempF=house_worst_case_temp_f,
            GNodeAlias=g_node_alias,
            FloParamsUid=flo_params_uid,
            #
        )

    @classmethod
    def tuple_to_type(cls, tuple: FloParamsBrickstorageheater) -> str:
        """
        Given a Python class object, returns the serialized JSON type object
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: str) -> FloParamsBrickstorageheater:
        """
        Given a serialized JSON type object, returns the Python class object
        """
        try:
            d = json.loads(t)
        except TypeError:
            raise SchemaError("Type must be string or bytes!")
        if not isinstance(d, dict):
            raise SchemaError(f"Deserializing {t} must result in dict!")
        return cls.dict_to_tuple(d)

    @classmethod
    def dict_to_tuple(cls, d: dict[str, Any]) -> FloParamsBrickstorageheater:
        d2 = dict(d)
        if "MaxBrickTempC" not in d2.keys():
            raise SchemaError(f"dict {d2} missing MaxBrickTempC")
        if "RatedMaxPowerKw" not in d2.keys():
            raise SchemaError(f"dict {d2} missing RatedMaxPowerKw")
        if "ROff" not in d2.keys():
            raise SchemaError(f"dict {d2} missing ROff")
        if "ROn" not in d2.keys():
            raise SchemaError(f"dict {d2} missing ROn")
        if "RoomTempF" not in d2.keys():
            raise SchemaError(f"dict {d2} missing RoomTempF")
        if "CurrencyUnitGtEnumSymbol" not in d2.keys():
            raise SchemaError(f"dict {d2} missing CurrencyUnitGtEnumSymbol")
        if (
            d2["CurrencyUnitGtEnumSymbol"]
            in RecognizedCurrencyUnit000SchemaEnum.symbols
        ):
            d2["CurrencyUnit"] = RecognizedCurrencyUnitMap.type_to_local(
                d2["CurrencyUnitGtEnumSymbol"]
            )
        else:
            d2["CurrencyUnit"] = RecognizedCurrencyUnit.default()
        if "TempUnitGtEnumSymbol" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TempUnitGtEnumSymbol")
        if d2["TempUnitGtEnumSymbol"] in RecognizedTemperatureUnit000SchemaEnum.symbols:
            d2["TempUnit"] = RecognizedTemperatureUnitMap.type_to_local(
                d2["TempUnitGtEnumSymbol"]
            )
        else:
            d2["TempUnit"] = RecognizedTemperatureUnit.default()
        if "TimezoneString" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TimezoneString")
        if "HomeCity" not in d2.keys():
            raise SchemaError(f"dict {d2} missing HomeCity")
        if "IsRegulating" not in d2.keys():
            raise SchemaError(f"dict {d2} missing IsRegulating")
        if "StorageSteps" not in d2.keys():
            raise SchemaError(f"dict {d2} missing StorageSteps")
        if "SliceDurationMinutes" not in d2.keys():
            raise SchemaError(f"dict {d2} missing SliceDurationMinutes")
        if "PowerRequiredByHouseFromSystemAvgKwList" not in d2.keys():
            raise SchemaError(
                f"dict {d2} missing PowerRequiredByHouseFromSystemAvgKwList"
            )
        if "C" not in d2.keys():
            d2["C"] = None
        if "RealtimeElectricityPrice" not in d2.keys():
            raise SchemaError(f"dict {d2} missing RealtimeElectricityPrice")
        if "OutsideTempF" not in d2.keys():
            raise SchemaError(f"dict {d2} missing OutsideTempF")
        if "DistributionPrice" not in d2.keys():
            raise SchemaError(f"dict {d2} missing DistributionPrice")
        if "RtElecPriceUid" not in d2.keys():
            raise SchemaError(f"dict {d2} missing RtElecPriceUid")
        if "RegulationPrice" not in d2.keys():
            raise SchemaError(f"dict {d2} missing RegulationPrice")
        if "WeatherUid" not in d2.keys():
            raise SchemaError(f"dict {d2} missing WeatherUid")
        if "DistPriceUid" not in d2.keys():
            d2["DistPriceUid"] = None
        if "RegPriceUid" not in d2.keys():
            d2["RegPriceUid"] = None
        if "StartYearUtc" not in d2.keys():
            raise SchemaError(f"dict {d2} missing StartYearUtc")
        if "StartMonthUtc" not in d2.keys():
            raise SchemaError(f"dict {d2} missing StartMonthUtc")
        if "StartDayUtc" not in d2.keys():
            raise SchemaError(f"dict {d2} missing StartDayUtc")
        if "StartHourUtc" not in d2.keys():
            raise SchemaError(f"dict {d2} missing StartHourUtc")
        if "StartMinuteUtc" not in d2.keys():
            raise SchemaError(f"dict {d2} missing StartMinuteUtc")
        if "StartingStoreIdx" not in d2.keys():
            raise SchemaError(f"dict {d2} missing StartingStoreIdx")
        if "AmbientPowerInKw" not in d2.keys():
            raise SchemaError(f"dict {d2} missing AmbientPowerInKw")
        if "HouseWorstCaseTempF" not in d2.keys():
            raise SchemaError(f"dict {d2} missing HouseWorstCaseTempF")
        if "GNodeAlias" not in d2.keys():
            raise SchemaError(f"dict {d2} missing GNodeAlias")
        if "FloParamsUid" not in d2.keys():
            raise SchemaError(f"dict {d2} missing FloParamsUid")
        if "TypeName" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TypeName")

        return FloParamsBrickstorageheater(
            MaxBrickTempC=d2["MaxBrickTempC"],
            RatedMaxPowerKw=d2["RatedMaxPowerKw"],
            ROff=d2["ROff"],
            ROn=d2["ROn"],
            RoomTempF=d2["RoomTempF"],
            CurrencyUnit=d2["CurrencyUnit"],
            TempUnit=d2["TempUnit"],
            TimezoneString=d2["TimezoneString"],
            HomeCity=d2["HomeCity"],
            IsRegulating=d2["IsRegulating"],
            StorageSteps=d2["StorageSteps"],
            SliceDurationMinutes=d2["SliceDurationMinutes"],
            PowerRequiredByHouseFromSystemAvgKwList=d2[
                "PowerRequiredByHouseFromSystemAvgKwList"
            ],
            C=d2["C"],
            RealtimeElectricityPrice=d2["RealtimeElectricityPrice"],
            OutsideTempF=d2["OutsideTempF"],
            DistributionPrice=d2["DistributionPrice"],
            RtElecPriceUid=d2["RtElecPriceUid"],
            RegulationPrice=d2["RegulationPrice"],
            WeatherUid=d2["WeatherUid"],
            DistPriceUid=d2["DistPriceUid"],
            RegPriceUid=d2["RegPriceUid"],
            StartYearUtc=d2["StartYearUtc"],
            StartMonthUtc=d2["StartMonthUtc"],
            StartDayUtc=d2["StartDayUtc"],
            StartHourUtc=d2["StartHourUtc"],
            StartMinuteUtc=d2["StartMinuteUtc"],
            StartingStoreIdx=d2["StartingStoreIdx"],
            AmbientPowerInKw=d2["AmbientPowerInKw"],
            HouseWorstCaseTempF=d2["HouseWorstCaseTempF"],
            GNodeAlias=d2["GNodeAlias"],
            FloParamsUid=d2["FloParamsUid"],
            TypeName=d2["TypeName"],
            Version="000",
        )
