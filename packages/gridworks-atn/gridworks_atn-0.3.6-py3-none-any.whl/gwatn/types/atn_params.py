"""Type atn.params, version 000"""
import json
from typing import Any
from typing import Dict
from typing import Literal

from gridworks.errors import SchemaError
from pydantic import BaseModel
from pydantic import Extra
from pydantic import Field
from pydantic import validator


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


class AtnParams(BaseModel):
    """Generic AtnParams.

    This is a partial type, which is expected to be satisfied by all types starting with atn.params
    (like atn.params.heatpumpwithbooststore). It is used to describe the generic info required for
    configuring an AtomicTNode.
    """

    GNodeAlias: str = Field(
        title="GNodeAlias",
    )
    HomeCity: str = Field(
        title="HomeCity",
        default="MILLINOCKET_ME",
    )
    TimezoneString: str = Field(
        title="TimezoneString",
        default="US/Eastern",
    )
    TypeName: str = Field(
        title="TypeName",
        default="atn.params",
    )
    Version: str = "000"

    class Config:
        extra = Extra.allow

    @validator("TypeName")
    def _check_type_name(cls, v: str) -> str:
        if not v.startswith("atn.params"):
            raise ValueError(f"TypeName {v} must start with 'atn.params'")
        return v

    @validator("GNodeAlias")
    def _check_g_node_alias(cls, v: str) -> str:
        try:
            check_is_left_right_dot(v)
        except ValueError as e:
            raise ValueError(f"GNodeAlias failed LeftRightDot format validation: {e}")
        return v

    def as_dict(self) -> Dict[str, Any]:
        d = self.dict()
        return d

    def as_type(self) -> str:
        return json.dumps(self.as_dict())

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class AtnParams_Maker:
    type_name = "atn.params"
    version = "000"

    def __init__(self, g_node_alias: str, home_city: str, timezone_string: str):
        self.tuple = AtnParams(
            GNodeAlias=g_node_alias,
            HomeCity=home_city,
            TimezoneString=timezone_string,
            #
        )

    @classmethod
    def tuple_to_type(cls, tuple: AtnParams) -> str:
        """
        Given a Python class object, returns the serialized JSON type object
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: str) -> AtnParams:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> AtnParams:
        d2 = dict(d)
        if "GNodeAlias" not in d2.keys():
            raise SchemaError(f"dict {d2} missing GNodeAlias")
        if "HomeCity" not in d2.keys():
            raise SchemaError(f"dict {d2} missing HomeCity")
        if "TimezoneString" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TimezoneString")
        if "TypeName" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TypeName")

        return AtnParams(
            GNodeAlias=d2["GNodeAlias"],
            HomeCity=d2["HomeCity"],
            TimezoneString=d2["TimezoneString"],
            TypeName=d2["TypeName"],
            Version="000",
        )
