"""Type simplesim.snapshot.brickstorageheater, version 000"""
import json
from typing import Any
from typing import Dict
from typing import Literal

from gridworks.errors import SchemaError
from pydantic import BaseModel
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


class SimplesimSnapshotBrickstorageheater(BaseModel):
    """ """

    FromGNodeAlias: str = Field(
        title="FromGNodeAlias",
    )
    FromGNodeInstanceId: str = Field(
        title="FromGNodeInstanceId",
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
    AboutTerminalAssetAlias: str = Field(
        title="AboutTerminalAssetAlias",
    )
    TypeName: Literal[
        "simplesim.snapshot.brickstorageheater"
    ] = "simplesim.snapshot.brickstorageheater"
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

    @validator("FromGNodeInstanceId")
    def _check_from_g_node_instance_id(cls, v: str) -> str:
        try:
            check_is_uuid_canonical_textual(v)
        except ValueError as e:
            raise ValueError(
                f"FromGNodeInstanceId failed UuidCanonicalTextual format validation: {e}"
            )
        return v

    @validator("AboutTerminalAssetAlias")
    def _check_about_terminal_asset_alias(cls, v: str) -> str:
        try:
            check_is_left_right_dot(v)
        except ValueError as e:
            raise ValueError(
                f"AboutTerminalAssetAlias failed LeftRightDot format validation: {e}"
            )
        return v

    def as_dict(self) -> Dict[str, Any]:
        d = self.dict()
        return d

    def as_type(self) -> str:
        return json.dumps(self.as_dict())

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class SimplesimSnapshotBrickstorageheater_Maker:
    type_name = "simplesim.snapshot.brickstorageheater"
    version = "000"

    def __init__(
        self,
        from_g_node_alias: str,
        from_g_node_instance_id: str,
        power_watts: int,
        store_kwh: int,
        max_store_kwh: int,
        about_terminal_asset_alias: str,
    ):
        self.tuple = SimplesimSnapshotBrickstorageheater(
            FromGNodeAlias=from_g_node_alias,
            FromGNodeInstanceId=from_g_node_instance_id,
            PowerWatts=power_watts,
            StoreKwh=store_kwh,
            MaxStoreKwh=max_store_kwh,
            AboutTerminalAssetAlias=about_terminal_asset_alias,
            #
        )

    @classmethod
    def tuple_to_type(cls, tuple: SimplesimSnapshotBrickstorageheater) -> str:
        """
        Given a Python class object, returns the serialized JSON type object
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: str) -> SimplesimSnapshotBrickstorageheater:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> SimplesimSnapshotBrickstorageheater:
        d2 = dict(d)
        if "FromGNodeAlias" not in d2.keys():
            raise SchemaError(f"dict {d2} missing FromGNodeAlias")
        if "FromGNodeInstanceId" not in d2.keys():
            raise SchemaError(f"dict {d2} missing FromGNodeInstanceId")
        if "PowerWatts" not in d2.keys():
            raise SchemaError(f"dict {d2} missing PowerWatts")
        if "StoreKwh" not in d2.keys():
            raise SchemaError(f"dict {d2} missing StoreKwh")
        if "MaxStoreKwh" not in d2.keys():
            raise SchemaError(f"dict {d2} missing MaxStoreKwh")
        if "AboutTerminalAssetAlias" not in d2.keys():
            raise SchemaError(f"dict {d2} missing AboutTerminalAssetAlias")
        if "TypeName" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TypeName")

        return SimplesimSnapshotBrickstorageheater(
            FromGNodeAlias=d2["FromGNodeAlias"],
            FromGNodeInstanceId=d2["FromGNodeInstanceId"],
            PowerWatts=d2["PowerWatts"],
            StoreKwh=d2["StoreKwh"],
            MaxStoreKwh=d2["MaxStoreKwh"],
            AboutTerminalAssetAlias=d2["AboutTerminalAssetAlias"],
            TypeName=d2["TypeName"],
            Version="000",
        )
