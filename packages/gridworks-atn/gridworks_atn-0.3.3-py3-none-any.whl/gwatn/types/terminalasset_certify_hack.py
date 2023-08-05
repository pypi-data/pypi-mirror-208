"""Type terminalasset.certify.hack, version 000"""
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


class TerminalassetCertifyHack(BaseModel):
    """ """

    TerminalAssetAlias: str = Field(
        title="TerminalAssetAlias",
    )
    TaDaemonApiPort: str = Field(
        title="TaDaemonApiPort",
    )
    TaDaemonApiFqdn: str = Field(
        title="TaDaemonApiFqdn",
    )
    TaDaemonAddr: str = Field(
        title="TaDaemonAddr",
    )
    TypeName: Literal["terminalasset.certify.hack"] = "terminalasset.certify.hack"
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

    @validator("TaDaemonAddr")
    def _check_ta_daemon_addr(cls, v: str) -> str:
        try:
            check_is_algo_address_string_format(v)
        except ValueError as e:
            raise ValueError(
                f"TaDaemonAddr failed AlgoAddressStringFormat format validation: {e}"
            )
        return v

    def as_dict(self) -> Dict[str, Any]:
        d = self.dict()
        return d

    def as_type(self) -> str:
        return json.dumps(self.as_dict())

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class TerminalassetCertifyHack_Maker:
    type_name = "terminalasset.certify.hack"
    version = "000"

    def __init__(
        self,
        terminal_asset_alias: str,
        ta_daemon_api_port: str,
        ta_daemon_api_fqdn: str,
        ta_daemon_addr: str,
    ):
        self.tuple = TerminalassetCertifyHack(
            TerminalAssetAlias=terminal_asset_alias,
            TaDaemonApiPort=ta_daemon_api_port,
            TaDaemonApiFqdn=ta_daemon_api_fqdn,
            TaDaemonAddr=ta_daemon_addr,
            #
        )

    @classmethod
    def tuple_to_type(cls, tuple: TerminalassetCertifyHack) -> str:
        """
        Given a Python class object, returns the serialized JSON type object
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: str) -> TerminalassetCertifyHack:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> TerminalassetCertifyHack:
        d2 = dict(d)
        if "TerminalAssetAlias" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TerminalAssetAlias")
        if "TaDaemonApiPort" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TaDaemonApiPort")
        if "TaDaemonApiFqdn" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TaDaemonApiFqdn")
        if "TaDaemonAddr" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TaDaemonAddr")
        if "TypeName" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TypeName")

        return TerminalassetCertifyHack(
            TerminalAssetAlias=d2["TerminalAssetAlias"],
            TaDaemonApiPort=d2["TaDaemonApiPort"],
            TaDaemonApiFqdn=d2["TaDaemonApiFqdn"],
            TaDaemonAddr=d2["TaDaemonAddr"],
            TypeName=d2["TypeName"],
            Version="000",
        )
