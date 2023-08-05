"""Type discoverycert.algo.create, version 000"""
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

from gwatn.enums import CoreGNodeRole


class CoreGNodeRole000SchemaEnum:
    enum_name: str = "core.g.node.role.000"
    symbols: List[str] = [
        "00000000",
        "0f8872f7",
        "d9823442",
        "86f21dd2",
        "9521af06",
        "4502e355",
        "d67e564e",
        "7a8e4046",
    ]

    @classmethod
    def is_symbol(cls, candidate: str) -> bool:
        if candidate in cls.symbols:
            return True
        return False


class CoreGNodeRole000(StrEnum):
    Other = auto()
    TerminalAsset = auto()
    AtomicTNode = auto()
    MarketMaker = auto()
    AtomicMeteringNode = auto()
    ConductorTopologyNode = auto()
    InterconnectionComponent = auto()
    Scada = auto()

    @classmethod
    def default(cls) -> "CoreGNodeRole000":
        return cls.Other

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]


class CoreGNodeRoleMap:
    @classmethod
    def type_to_local(cls, symbol: str) -> CoreGNodeRole:
        if not CoreGNodeRole000SchemaEnum.is_symbol(symbol):
            raise SchemaError(f"{symbol} must belong to CoreGNodeRole000 symbols")
        versioned_enum = cls.type_to_versioned_enum_dict[symbol]
        return as_enum(versioned_enum, CoreGNodeRole, CoreGNodeRole.default())

    @classmethod
    def local_to_type(cls, core_g_node_role: CoreGNodeRole) -> str:
        if not isinstance(core_g_node_role, CoreGNodeRole):
            raise SchemaError(f"{core_g_node_role} must be of type {CoreGNodeRole}")
        versioned_enum = as_enum(
            core_g_node_role, CoreGNodeRole000, CoreGNodeRole000.default()
        )
        return cls.versioned_enum_to_type_dict[versioned_enum]

    type_to_versioned_enum_dict: Dict[str, CoreGNodeRole000] = {
        "00000000": CoreGNodeRole000.Other,
        "0f8872f7": CoreGNodeRole000.TerminalAsset,
        "d9823442": CoreGNodeRole000.AtomicTNode,
        "86f21dd2": CoreGNodeRole000.MarketMaker,
        "9521af06": CoreGNodeRole000.AtomicMeteringNode,
        "4502e355": CoreGNodeRole000.ConductorTopologyNode,
        "d67e564e": CoreGNodeRole000.InterconnectionComponent,
        "7a8e4046": CoreGNodeRole000.Scada,
    }

    versioned_enum_to_type_dict: Dict[CoreGNodeRole000, str] = {
        CoreGNodeRole000.Other: "00000000",
        CoreGNodeRole000.TerminalAsset: "0f8872f7",
        CoreGNodeRole000.AtomicTNode: "d9823442",
        CoreGNodeRole000.MarketMaker: "86f21dd2",
        CoreGNodeRole000.AtomicMeteringNode: "9521af06",
        CoreGNodeRole000.ConductorTopologyNode: "4502e355",
        CoreGNodeRole000.InterconnectionComponent: "d67e564e",
        CoreGNodeRole000.Scada: "7a8e4046",
    }


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


def check_is_algo_address_string_format(v: str) -> None:
    """
    AlgoAddressStringFormat format: The public key of a private/public Ed25519
    key pair, transformed into an  Algorand address, by adding a 4-byte checksum
    to the end of the public key and then encoding in base32.

    Raises:
        ValueError: if not AlgoAddressStringFormat format
    """
    import algosdk

    at = algosdk.abi.AddressType()
    try:
        result = at.decode(at.encode(v))
    except Exception as e:
        raise ValueError(f"Not AlgoAddressStringFormat: {e}")


class DiscoverycertAlgoCreate(BaseModel):
    """ """

    GNodeAlias: str = Field(
        title="GNodeAlias",
    )
    Role: CoreGNodeRole = Field(
        title="Role",
    )
    OldChildAliasList: List[str] = Field(
        title="OldChildAliasList",
    )
    DiscovererAddr: str = Field(
        title="DiscovererAddr",
    )
    SupportingMaterialHash: str = Field(
        title="SupportingMaterialHash",
    )
    MicroLat: Optional[int] = Field(
        title="MicroLat",
        default=None,
    )
    MicroLon: Optional[int] = Field(
        title="MicroLon",
        default=None,
    )
    TypeName: Literal["discoverycert.algo.create"] = "discoverycert.algo.create"
    Version: str = "000"

    @validator("GNodeAlias")
    def _check_g_node_alias(cls, v: str) -> str:
        try:
            check_is_left_right_dot(v)
        except ValueError as e:
            raise ValueError(f"GNodeAlias failed LeftRightDot format validation: {e}")
        return v

    @validator("Role")
    def _check_role(cls, v: CoreGNodeRole) -> CoreGNodeRole:
        return as_enum(v, CoreGNodeRole, CoreGNodeRole.Other)

    @validator("OldChildAliasList")
    def _check_old_child_alias_list(cls, v: List) -> List:
        for elt in v:
            try:
                check_is_left_right_dot(elt)
            except ValueError as e:
                raise ValueError(
                    f"OldChildAliasList element {elt} failed LeftRightDot format validation: {e}"
                )
        return v

    @validator("DiscovererAddr")
    def _check_discoverer_addr(cls, v: str) -> str:
        try:
            check_is_algo_address_string_format(v)
        except ValueError as e:
            raise ValueError(
                f"DiscovererAddr failed AlgoAddressStringFormat format validation: {e}"
            )
        return v

    def as_dict(self) -> Dict[str, Any]:
        d = self.dict()
        del d["Role"]
        Role = as_enum(self.Role, CoreGNodeRole, CoreGNodeRole.default())
        d["RoleGtEnumSymbol"] = CoreGNodeRoleMap.local_to_type(Role)
        if d["MicroLat"] is None:
            del d["MicroLat"]
        if d["MicroLon"] is None:
            del d["MicroLon"]
        return d

    def as_type(self) -> str:
        return json.dumps(self.as_dict())

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class DiscoverycertAlgoCreate_Maker:
    type_name = "discoverycert.algo.create"
    version = "000"

    def __init__(
        self,
        g_node_alias: str,
        role: CoreGNodeRole,
        old_child_alias_list: List[str],
        discoverer_addr: str,
        supporting_material_hash: str,
        micro_lat: Optional[int],
        micro_lon: Optional[int],
    ):
        self.tuple = DiscoverycertAlgoCreate(
            GNodeAlias=g_node_alias,
            Role=role,
            OldChildAliasList=old_child_alias_list,
            DiscovererAddr=discoverer_addr,
            SupportingMaterialHash=supporting_material_hash,
            MicroLat=micro_lat,
            MicroLon=micro_lon,
            #
        )

    @classmethod
    def tuple_to_type(cls, tuple: DiscoverycertAlgoCreate) -> str:
        """
        Given a Python class object, returns the serialized JSON type object
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: str) -> DiscoverycertAlgoCreate:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> DiscoverycertAlgoCreate:
        d2 = dict(d)
        if "GNodeAlias" not in d2.keys():
            raise SchemaError(f"dict {d2} missing GNodeAlias")
        if "RoleGtEnumSymbol" not in d2.keys():
            raise SchemaError(f"dict {d2} missing RoleGtEnumSymbol")
        if d2["RoleGtEnumSymbol"] in CoreGNodeRole000SchemaEnum.symbols:
            d2["Role"] = CoreGNodeRoleMap.type_to_local(d2["RoleGtEnumSymbol"])
        else:
            d2["Role"] = CoreGNodeRole.default()
        if "OldChildAliasList" not in d2.keys():
            raise SchemaError(f"dict {d2} missing OldChildAliasList")
        if "DiscovererAddr" not in d2.keys():
            raise SchemaError(f"dict {d2} missing DiscovererAddr")
        if "SupportingMaterialHash" not in d2.keys():
            raise SchemaError(f"dict {d2} missing SupportingMaterialHash")
        if "MicroLat" not in d2.keys():
            d2["MicroLat"] = None
        if "MicroLon" not in d2.keys():
            d2["MicroLon"] = None
        if "TypeName" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TypeName")

        return DiscoverycertAlgoCreate(
            GNodeAlias=d2["GNodeAlias"],
            Role=d2["Role"],
            OldChildAliasList=d2["OldChildAliasList"],
            DiscovererAddr=d2["DiscovererAddr"],
            SupportingMaterialHash=d2["SupportingMaterialHash"],
            MicroLat=d2["MicroLat"],
            MicroLon=d2["MicroLon"],
            TypeName=d2["TypeName"],
            Version="000",
        )
