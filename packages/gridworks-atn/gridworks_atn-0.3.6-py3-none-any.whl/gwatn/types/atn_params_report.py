"""Type atn.params.report, version 000"""
import json
from typing import Any
from typing import Dict
from typing import Literal
from typing import Optional

from gridworks.errors import SchemaError
from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from gwatn.types.atn_params import AtnParams
from gwatn.types.atn_params import AtnParams_Maker


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


class AtnParamsReport(BaseModel):
    """AtomicTNode reporting its AtnParams.

    Parameters like the size of the thermal store.
    """

    GNodeAlias: str = Field(
        title="GNodeAlias",
    )
    GNodeInstanceId: str = Field(
        title="GNodeInstanceId",
    )
    AtnParamsTypeName: str = Field(
        title="AtnParamsTypeName",
    )
    TimeUnixS: int = Field(
        title="TimeUnixS",
    )
    IrlTimeUnixS: Optional[int] = Field(
        title="IrlTimeUnixS",
        default=None,
    )
    Params: AtnParams = Field(
        title="Params",
    )
    TypeName: Literal["atn.params.report"] = "atn.params.report"
    Version: str = "000"

    @validator("GNodeAlias")
    def _check_g_node_alias(cls, v: str) -> str:
        try:
            check_is_left_right_dot(v)
        except ValueError as e:
            raise ValueError(f"GNodeAlias failed LeftRightDot format validation: {e}")
        return v

    @validator("GNodeInstanceId")
    def _check_g_node_instance_id(cls, v: str) -> str:
        try:
            check_is_uuid_canonical_textual(v)
        except ValueError as e:
            raise ValueError(
                f"GNodeInstanceId failed UuidCanonicalTextual format validation: {e}"
            )
        return v

    @validator("AtnParamsTypeName")
    def _check_atn_params_type_name(cls, v: str) -> str:
        try:
            check_is_left_right_dot(v)
        except ValueError as e:
            raise ValueError(
                f"AtnParamsTypeName failed LeftRightDot format validation: {e}"
            )
        return v

    @validator("TimeUnixS")
    def _check_time_unix_s(cls, v: int) -> int:
        try:
            check_is_reasonable_unix_time_s(v)
        except ValueError as e:
            raise ValueError(
                f"TimeUnixS failed ReasonableUnixTimeS format validation: {e}"
            )
        return v

    @validator("IrlTimeUnixS")
    def _check_irl_time_unix_s(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        try:
            check_is_reasonable_unix_time_s(v)
        except ValueError as e:
            raise ValueError(
                f"IrlTimeUnixS failed ReasonableUnixTimeS format validation: {e}"
            )
        return v

    def as_dict(self) -> Dict[str, Any]:
        d = self.dict()
        if d["IrlTimeUnixS"] is None:
            del d["IrlTimeUnixS"]
        d["Params"] = self.Params.as_dict()
        return d

    def as_type(self) -> str:
        return json.dumps(self.as_dict())

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class AtnParamsReport_Maker:
    type_name = "atn.params.report"
    version = "000"

    def __init__(
        self,
        g_node_alias: str,
        g_node_instance_id: str,
        atn_params_type_name: str,
        time_unix_s: int,
        irl_time_unix_s: Optional[int],
        params: AtnParams,
    ):
        self.tuple = AtnParamsReport(
            GNodeAlias=g_node_alias,
            GNodeInstanceId=g_node_instance_id,
            AtnParamsTypeName=atn_params_type_name,
            TimeUnixS=time_unix_s,
            IrlTimeUnixS=irl_time_unix_s,
            Params=params,
            #
        )

    @classmethod
    def tuple_to_type(cls, tuple: AtnParamsReport) -> str:
        """
        Given a Python class object, returns the serialized JSON type object
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: str) -> AtnParamsReport:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> AtnParamsReport:
        d2 = dict(d)
        if "GNodeAlias" not in d2.keys():
            raise SchemaError(f"dict {d2} missing GNodeAlias")
        if "GNodeInstanceId" not in d2.keys():
            raise SchemaError(f"dict {d2} missing GNodeInstanceId")
        if "AtnParamsTypeName" not in d2.keys():
            raise SchemaError(f"dict {d2} missing AtnParamsTypeName")
        if "TimeUnixS" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TimeUnixS")
        if "IrlTimeUnixS" not in d2.keys():
            d2["IrlTimeUnixS"] = None
        if "Params" not in d2.keys():
            raise SchemaError(f"dict {d2} missing Params")
        if not isinstance(d2["Params"], dict):
            raise SchemaError(f"d['Params'] {d2['Params']} must be a AtnParams!")
        params = AtnParams_Maker.dict_to_tuple(d2["Params"])
        d2["Params"] = params
        if "TypeName" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TypeName")

        return AtnParamsReport(
            GNodeAlias=d2["GNodeAlias"],
            GNodeInstanceId=d2["GNodeInstanceId"],
            AtnParamsTypeName=d2["AtnParamsTypeName"],
            TimeUnixS=d2["TimeUnixS"],
            IrlTimeUnixS=d2["IrlTimeUnixS"],
            Params=d2["Params"],
            TypeName=d2["TypeName"],
            Version="000",
        )
