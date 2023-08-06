"""Type flo.params, version 000"""
import json
from typing import Any
from typing import Dict
from typing import Literal

from gridworks.errors import SchemaError
from pydantic import BaseModel
from pydantic import Extra
from pydantic import Field
from pydantic import validator


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


class FloParams(BaseModel):
    """Base class for Forward Looking Optimizer params.

    Derived classes are expected to have TypeNames enforced as literals that start with flo.params. E.g. flo.params.brickstorageheater.   This container is used for sending messages that include flo.params (i.e, flo.params.report
    [More info](https://gridworks-atn.readthedocs.io/en/latest/flo.html#flo-params).
    """

    GNodeAlias: str = Field(
        title="GNodeAlias",
    )
    FloParamsUid: str = Field(
        title="FloParamsUid",
    )
    HomeCity: str = Field(
        title="HomeCity",
        default="MILLINOCKET_ME",
    )
    TimezoneString: str = Field(
        title="TimezoneString",
        default="US/Eastern",
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
    TypeName: str = Field(
        title="TypeName",
        default="flo.params",
    )
    Version: str = "000"

    class Config:
        extra = Extra.allow

    @validator("TypeName")
    def _check_type_name(cls, v: str) -> str:
        if not v.startswith("flo.params"):
            raise ValueError(f"TypeName {v} must start with 'flo.params'")
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
        return d

    def as_type(self) -> str:
        return json.dumps(self.as_dict())

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class FloParams_Maker:
    type_name = "flo.params"
    version = "000"

    def __init__(
        self,
        g_node_alias: str,
        flo_params_uid: str,
        home_city: str,
        timezone_string: str,
        start_year_utc: int,
        start_month_utc: int,
        start_day_utc: int,
        start_hour_utc: int,
        start_minute_utc: int,
    ):
        self.tuple = FloParams(
            GNodeAlias=g_node_alias,
            FloParamsUid=flo_params_uid,
            HomeCity=home_city,
            TimezoneString=timezone_string,
            StartYearUtc=start_year_utc,
            StartMonthUtc=start_month_utc,
            StartDayUtc=start_day_utc,
            StartHourUtc=start_hour_utc,
            StartMinuteUtc=start_minute_utc,
            #
        )

    @classmethod
    def tuple_to_type(cls, tuple: FloParams) -> str:
        """
        Given a Python class object, returns the serialized JSON type object
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: str) -> FloParams:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> FloParams:
        d2 = dict(d)
        if "GNodeAlias" not in d2.keys():
            raise SchemaError(f"dict {d2} missing GNodeAlias")
        if "FloParamsUid" not in d2.keys():
            raise SchemaError(f"dict {d2} missing FloParamsUid")
        if "HomeCity" not in d2.keys():
            raise SchemaError(f"dict {d2} missing HomeCity")
        if "TimezoneString" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TimezoneString")
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
        if "TypeName" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TypeName")

        return FloParams(
            GNodeAlias=d2["GNodeAlias"],
            FloParamsUid=d2["FloParamsUid"],
            HomeCity=d2["HomeCity"],
            TimezoneString=d2["TimezoneString"],
            StartYearUtc=d2["StartYearUtc"],
            StartMonthUtc=d2["StartMonthUtc"],
            StartDayUtc=d2["StartDayUtc"],
            StartHourUtc=d2["StartHourUtc"],
            StartMinuteUtc=d2["StartMinuteUtc"],
            TypeName=d2["TypeName"],
            Version="000",
        )
