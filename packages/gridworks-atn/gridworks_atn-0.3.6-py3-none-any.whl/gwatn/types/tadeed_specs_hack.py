"""Type tadeed.specs.hack, version 000"""
import json
from typing import Any
from typing import Dict
from typing import Literal

from gridworks.errors import SchemaError
from pydantic import BaseModel
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


class TadeedSpecsHack(BaseModel):
    """ """

    TerminalAssetAlias: str = Field(
        title="TerminalAssetAlias",
    )
    MicroLat: int = Field(
        title="MicroLat",
    )
    MicroLon: int = Field(
        title="MicroLon",
    )
    DaemonPort: int = Field(
        title="DaemonPort",
    )
    TypeName: Literal["tadeed.specs.hack"] = "tadeed.specs.hack"
    Version: str = "000"

    @validator("TerminalAssetAlias")
    def _check_terminal_asset_alias(cls, v: str) -> str:
        try:
            check_is_left_right_dot(v)
        except ValueError as e:
            raise ValueError(
                f"TerminalAssetAlias failed LeftRightDot format validation: {e}"
            )
        return v

    def as_dict(self) -> Dict[str, Any]:
        d = self.dict()
        return d

    def as_type(self) -> str:
        return json.dumps(self.as_dict())

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class TadeedSpecsHack_Maker:
    type_name = "tadeed.specs.hack"
    version = "000"

    def __init__(
        self,
        terminal_asset_alias: str,
        micro_lat: int,
        micro_lon: int,
        daemon_port: int,
    ):
        self.tuple = TadeedSpecsHack(
            TerminalAssetAlias=terminal_asset_alias,
            MicroLat=micro_lat,
            MicroLon=micro_lon,
            DaemonPort=daemon_port,
            #
        )

    @classmethod
    def tuple_to_type(cls, tuple: TadeedSpecsHack) -> str:
        """
        Given a Python class object, returns the serialized JSON type object
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: str) -> TadeedSpecsHack:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> TadeedSpecsHack:
        d2 = dict(d)
        if "TerminalAssetAlias" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TerminalAssetAlias")
        if "MicroLat" not in d2.keys():
            raise SchemaError(f"dict {d2} missing MicroLat")
        if "MicroLon" not in d2.keys():
            raise SchemaError(f"dict {d2} missing MicroLon")
        if "DaemonPort" not in d2.keys():
            raise SchemaError(f"dict {d2} missing DaemonPort")
        if "TypeName" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TypeName")

        return TadeedSpecsHack(
            TerminalAssetAlias=d2["TerminalAssetAlias"],
            MicroLat=d2["MicroLat"],
            MicroLon=d2["MicroLon"],
            DaemonPort=d2["DaemonPort"],
            TypeName=d2["TypeName"],
            Version="000",
        )
