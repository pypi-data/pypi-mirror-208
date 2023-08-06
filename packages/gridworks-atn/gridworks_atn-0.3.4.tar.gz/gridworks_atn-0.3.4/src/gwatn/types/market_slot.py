"""Type market.slot, version 000"""
import json
from typing import Any
from typing import Dict
from typing import Literal

from gridworks.errors import SchemaError
from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from gwatn.types.market_type_gt import MarketTypeGt
from gwatn.types.market_type_gt import MarketTypeGt_Maker


def check_is_reasonable_unix_time_s(v: int) -> None:
    """
    ReasonableUnixTimeS format: time in unix seconds between Jan 1 2000 and Jan 1 3000

    Raises:
        ValueError: if not ReasonableUnixTimeS format
    """
    import pendulum

    if pendulum.parse("2000-01-01T00:00:00Z").int_timestamp > v:  # type: ignore[attr-defined]
        raise ValueError(f"{v} must be after Jan 1 2000")
    if pendulum.parse("3000-01-01T00:00:00Z").int_timestamp < v:  # type: ignore[attr-defined]
        raise ValueError(f"{v} must be before Jan 1 3000")


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


class MarketSlot(BaseModel):
    """MarketSlot
    [More info](https://gridworks.readthedocs.io/en/latest/market-slot.html).
    """

    Type: MarketTypeGt = Field(
        title="Type",
    )
    MarketMakerAlias: str = Field(
        title="MarketMakerAlias",
    )
    StartUnixS: int = Field(
        title="StartUnixS",
    )
    TypeName: Literal["market.slot"] = "market.slot"
    Version: str = "000"

    @validator("MarketMakerAlias")
    def _check_market_maker_alias(cls, v: str) -> str:
        try:
            check_is_left_right_dot(v)
        except ValueError as e:
            raise ValueError(
                f"MarketMakerAlias failed LeftRightDot format validation: {e}"
            )
        return v

    @validator("StartUnixS")
    def _check_start_unix_s(cls, v: int) -> int:
        try:
            check_is_reasonable_unix_time_s(v)
        except ValueError as e:
            raise ValueError(
                f"StartUnixS failed ReasonableUnixTimeS format validation: {e}"
            )
        return v

    def as_dict(self) -> Dict[str, Any]:
        d = self.dict()
        d["Type"] = self.Type.as_dict()
        return d

    def as_type(self) -> str:
        return json.dumps(self.as_dict())

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class MarketSlot_Maker:
    type_name = "market.slot"
    version = "000"

    def __init__(self, type: MarketTypeGt, market_maker_alias: str, start_unix_s: int):
        self.tuple = MarketSlot(
            Type=type,
            MarketMakerAlias=market_maker_alias,
            StartUnixS=start_unix_s,
            #
        )

    @classmethod
    def tuple_to_type(cls, tuple: MarketSlot) -> str:
        """
        Given a Python class object, returns the serialized JSON type object
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: str) -> MarketSlot:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> MarketSlot:
        d2 = dict(d)
        if "Type" not in d2.keys():
            raise SchemaError(f"dict {d2} missing Type")
        if not isinstance(d2["Type"], dict):
            raise SchemaError(f"d['Type'] {d2['Type']} must be a MarketTypeGt!")
        type = MarketTypeGt_Maker.dict_to_tuple(d2["Type"])
        d2["Type"] = type
        if "MarketMakerAlias" not in d2.keys():
            raise SchemaError(f"dict {d2} missing MarketMakerAlias")
        if "StartUnixS" not in d2.keys():
            raise SchemaError(f"dict {d2} missing StartUnixS")
        if "TypeName" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TypeName")

        return MarketSlot(
            Type=d2["Type"],
            MarketMakerAlias=d2["MarketMakerAlias"],
            StartUnixS=d2["StartUnixS"],
            TypeName=d2["TypeName"],
            Version="000",
        )
