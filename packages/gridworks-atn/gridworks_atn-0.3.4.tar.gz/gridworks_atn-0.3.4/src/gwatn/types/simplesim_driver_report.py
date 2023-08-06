"""Type simplesim.driver.report, version 000"""
import json
from typing import Any
from typing import Dict
from typing import Literal

from gridworks.errors import SchemaError
from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from gwatn.types.simplesim_driver_data import SimplesimDriverData
from gwatn.types.simplesim_driver_data import SimplesimDriverData_Maker


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


class SimplesimDriverReport(BaseModel):
    """ """

    FromGNodeAlias: str = Field(
        title="FromGNodeAlias",
    )
    FromGNodeInstanecId: str = Field(
        title="FromGNodeInstanecId",
    )
    DriverDataTypeName: str = Field(
        title="DriverDataTypeName",
    )
    DriverData: SimplesimDriverData = Field(
        title="DriverData",
    )
    TypeName: Literal["simplesim.driver.report"] = "simplesim.driver.report"
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

    @validator("FromGNodeInstanecId")
    def _check_from_g_node_instanec_id(cls, v: str) -> str:
        try:
            check_is_uuid_canonical_textual(v)
        except ValueError as e:
            raise ValueError(
                f"FromGNodeInstanecId failed UuidCanonicalTextual format validation: {e}"
            )
        return v

    @validator("DriverDataTypeName")
    def _check_driver_data_type_name(cls, v: str) -> str:
        try:
            check_is_left_right_dot(v)
        except ValueError as e:
            raise ValueError(
                f"DriverDataTypeName failed LeftRightDot format validation: {e}"
            )
        return v

    def as_dict(self) -> Dict[str, Any]:
        d = self.dict()
        d["DriverData"] = self.DriverData.as_dict()
        return d

    def as_type(self) -> str:
        return json.dumps(self.as_dict())

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class SimplesimDriverReport_Maker:
    type_name = "simplesim.driver.report"
    version = "000"

    def __init__(
        self,
        from_g_node_alias: str,
        from_g_node_instanec_id: str,
        driver_data_type_name: str,
        driver_data: SimplesimDriverData,
    ):
        self.tuple = SimplesimDriverReport(
            FromGNodeAlias=from_g_node_alias,
            FromGNodeInstanecId=from_g_node_instanec_id,
            DriverDataTypeName=driver_data_type_name,
            DriverData=driver_data,
            #
        )

    @classmethod
    def tuple_to_type(cls, tuple: SimplesimDriverReport) -> str:
        """
        Given a Python class object, returns the serialized JSON type object
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: str) -> SimplesimDriverReport:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> SimplesimDriverReport:
        d2 = dict(d)
        if "FromGNodeAlias" not in d2.keys():
            raise SchemaError(f"dict {d2} missing FromGNodeAlias")
        if "FromGNodeInstanecId" not in d2.keys():
            raise SchemaError(f"dict {d2} missing FromGNodeInstanecId")
        if "DriverDataTypeName" not in d2.keys():
            raise SchemaError(f"dict {d2} missing DriverDataTypeName")
        if "DriverData" not in d2.keys():
            raise SchemaError(f"dict {d2} missing DriverData")
        if not isinstance(d2["DriverData"], dict):
            raise SchemaError(
                f"d['DriverData'] {d2['DriverData']} must be a SimplesimDriverData!"
            )
        driver_data = SimplesimDriverData_Maker.dict_to_tuple(d2["DriverData"])
        d2["DriverData"] = driver_data
        if "TypeName" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TypeName")

        return SimplesimDriverReport(
            FromGNodeAlias=d2["FromGNodeAlias"],
            FromGNodeInstanecId=d2["FromGNodeInstanecId"],
            DriverDataTypeName=d2["DriverDataTypeName"],
            DriverData=d2["DriverData"],
            TypeName=d2["TypeName"],
            Version="000",
        )
