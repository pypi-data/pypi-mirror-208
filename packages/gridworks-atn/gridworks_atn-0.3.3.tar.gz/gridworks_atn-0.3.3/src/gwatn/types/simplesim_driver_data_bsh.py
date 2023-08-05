"""Type simplesim.driver.data.bsh, version 000"""
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


class SimplesimDriverDataBsh(BaseModel):
    """ """

    FromGNodeAlias: str = Field(
        title="FromGNodeAlias",
    )
    PowerWatts: int = Field(
        title="PowerWatts",
    )
    StoreKwh: int = Field(
        title="StoreKwh",
    )
    MaxStoreKwh: int = Field(
        title="MaxStoreKwh",
    )
    TypeName: Literal["simplesim.driver.data.bsh"] = "simplesim.driver.data.bsh"
    Version: str = "000"

    @validator("FromGNodeAlias")
    def _check_from_g_node_alias(cls, v: str) -> str:
        try:
            check_is_left_right_dot(v)
        except ValueError as e:
            raise ValueError(
                f"FromGNodeAlias failed LeftRightDot format validation: {e}"
            )
        return v

    def as_dict(self) -> Dict[str, Any]:
        d = self.dict()
        return d

    def as_type(self) -> str:
        return json.dumps(self.as_dict())

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class SimplesimDriverDataBsh_Maker:
    type_name = "simplesim.driver.data.bsh"
    version = "000"

    def __init__(
        self,
        from_g_node_alias: str,
        power_watts: int,
        store_kwh: int,
        max_store_kwh: int,
    ):
        self.tuple = SimplesimDriverDataBsh(
            FromGNodeAlias=from_g_node_alias,
            PowerWatts=power_watts,
            StoreKwh=store_kwh,
            MaxStoreKwh=max_store_kwh,
            #
        )

    @classmethod
    def tuple_to_type(cls, tuple: SimplesimDriverDataBsh) -> str:
        """
        Given a Python class object, returns the serialized JSON type object
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: str) -> SimplesimDriverDataBsh:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> SimplesimDriverDataBsh:
        d2 = dict(d)
        if "FromGNodeAlias" not in d2.keys():
            raise SchemaError(f"dict {d2} missing FromGNodeAlias")
        if "PowerWatts" not in d2.keys():
            raise SchemaError(f"dict {d2} missing PowerWatts")
        if "StoreKwh" not in d2.keys():
            raise SchemaError(f"dict {d2} missing StoreKwh")
        if "MaxStoreKwh" not in d2.keys():
            raise SchemaError(f"dict {d2} missing MaxStoreKwh")
        if "TypeName" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TypeName")

        return SimplesimDriverDataBsh(
            FromGNodeAlias=d2["FromGNodeAlias"],
            PowerWatts=d2["PowerWatts"],
            StoreKwh=d2["StoreKwh"],
            MaxStoreKwh=d2["MaxStoreKwh"],
            TypeName=d2["TypeName"],
            Version="000",
        )
