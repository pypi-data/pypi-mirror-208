"""Type basegnode.scada.create, version 000"""
import json
from typing import Any
from typing import Dict
from typing import Literal

from gridworks.errors import SchemaError
from pydantic import BaseModel
from pydantic import Field
from pydantic import root_validator
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


def check_is_algo_msg_pack_encoded(v: str) -> None:
    """
    AlgoMSgPackEncoded format: the format of an  transaction sent to
    the Algorand blockchain.

    Raises:
        ValueError: if not AlgoMSgPackEncoded  format
    """
    import algosdk

    try:
        algosdk.encoding.future_msgpack_decode(v)
    except Exception as e:
        raise ValueError(f"Not AlgoMsgPackEncoded format: {e}")


class BasegnodeScadaCreate(BaseModel):
    """Scada BaseGNode Creation.

    This is a payload designed to be sent from a TaOwner to the GNodeFactory. The TaOwner creates a private Algorand key and puts it on the Scada Device that will sense and control their TerminalAsset. The public address is associated with the Scada GNode by the GNodeFactory.
    """

    TaAlias: str = Field(
        title="TerminalAsset Alias",
        description="GNodeAlias of the TerminalAsset that will be controlled by the new SCADA GNode. The SCADA GNodeAlias will have '.scada' appended to this.",
    )
    ScadaAddr: str = Field(
        title="Algorand address for the SCADA",
        description="The TaOwner makes the corresponding private key, puts it on the SCADA device, and then sends this address to the GNodeFactory.",
    )
    TaDaemonAddr: str = Field(
        title="Algorand address of the associated TaDaemon",
        description="The TaDaemonAddr will have the TaDeed, and can be used to verify the public address of the TaOwner",
    )
    GNodeRegistryAddr: str = Field(
        title="GNodeRegistry Algorand address",
        description="The GNodeRegistry that contains Make/Model information about the SCADA and TerminalAsset",
    )
    SignedProof: str = Field(
        title="Recent transaction signed by the TaOwner",
        description="These will be replaced by composite transactions in next gen code.",
    )
    TypeName: Literal["basegnode.scada.create"] = "basegnode.scada.create"
    Version: str = "000"

    @validator("TaAlias")
    def _check_ta_alias(cls, v: str) -> str:
        try:
            check_is_left_right_dot(v)
        except ValueError as e:
            raise ValueError(f"TaAlias failed LeftRightDot format validation: {e}")
        return v

    @validator("ScadaAddr")
    def _check_scada_addr(cls, v: str) -> str:
        try:
            check_is_algo_address_string_format(v)
        except ValueError as e:
            raise ValueError(
                f"ScadaAddr failed AlgoAddressStringFormat format validation: {e}"
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

    @validator("GNodeRegistryAddr")
    def _check_g_node_registry_addr(cls, v: str) -> str:
        try:
            check_is_algo_address_string_format(v)
        except ValueError as e:
            raise ValueError(
                f"GNodeRegistryAddr failed AlgoAddressStringFormat format validation: {e}"
            )
        return v

    @validator("SignedProof")
    def _check_signed_proof(cls, v: str) -> str:
        try:
            check_is_algo_msg_pack_encoded(v)
        except ValueError as e:
            raise ValueError(
                f"SignedProof failed AlgoMsgPackEncoded format validation: {e}"
            )
        return v

    @root_validator
    def check_axiom_1(cls, v: dict) -> dict:
        """
        Axiom 1: TaOwner is SignedProof signer.
        The TaDaemonAddr provides the public address for the TaOwner. This TaOwnerAddr must match
        the signature on the SignedProof.
        """
        # TODO: Implement check for axiom 1"
        return v

    @root_validator
    def check_axiom_2(cls, v: dict) -> dict:
        """
        Axiom 2: TaAlias matches TaDeed.
        The TaDaemonAddr owns a TaDeed for the TaAlias.
        """
        # TODO: Implement check for axiom 2"
        return v

    def as_dict(self) -> Dict[str, Any]:
        d = self.dict()
        return d

    def as_type(self) -> str:
        return json.dumps(self.as_dict())

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class BasegnodeScadaCreate_Maker:
    type_name = "basegnode.scada.create"
    version = "000"

    def __init__(
        self,
        ta_alias: str,
        scada_addr: str,
        ta_daemon_addr: str,
        g_node_registry_addr: str,
        signed_proof: str,
    ):
        self.tuple = BasegnodeScadaCreate(
            TaAlias=ta_alias,
            ScadaAddr=scada_addr,
            TaDaemonAddr=ta_daemon_addr,
            GNodeRegistryAddr=g_node_registry_addr,
            SignedProof=signed_proof,
            #
        )

    @classmethod
    def tuple_to_type(cls, tuple: BasegnodeScadaCreate) -> str:
        """
        Given a Python class object, returns the serialized JSON type object
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: str) -> BasegnodeScadaCreate:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> BasegnodeScadaCreate:
        d2 = dict(d)
        if "TaAlias" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TaAlias")
        if "ScadaAddr" not in d2.keys():
            raise SchemaError(f"dict {d2} missing ScadaAddr")
        if "TaDaemonAddr" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TaDaemonAddr")
        if "GNodeRegistryAddr" not in d2.keys():
            raise SchemaError(f"dict {d2} missing GNodeRegistryAddr")
        if "SignedProof" not in d2.keys():
            raise SchemaError(f"dict {d2} missing SignedProof")
        if "TypeName" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TypeName")

        return BasegnodeScadaCreate(
            TaAlias=d2["TaAlias"],
            ScadaAddr=d2["ScadaAddr"],
            TaDaemonAddr=d2["TaDaemonAddr"],
            GNodeRegistryAddr=d2["GNodeRegistryAddr"],
            SignedProof=d2["SignedProof"],
            TypeName=d2["TypeName"],
            Version="000",
        )
