"""Type scada.cert.transfer, version 000"""
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


class ScadaCertTransfer(BaseModel):
    """Scada Certificate Transfer.

    This is a payload designed to be sent from a SCADA device to the GNodeFactory after the SCADA has opted into its certificate.
    """

    TaAlias: str = Field(
        title="TerminalAsset Alias",
        description="GNodeAlias of the TerminalAsset for which the SCADA certificate is issued. The ScadaCert can be found from this.",
    )
    SignedProof: str = Field(
        title="Signed Proof from the SCADA Actor",
        description="The Scada GNode has a ScadaAlgoAddr in the GNodeFactory database, and the identity of the SCADA actor can be verified by this.",
    )
    TypeName: Literal["scada.cert.transfer"] = "scada.cert.transfer"
    Version: str = "000"

    @validator("TaAlias")
    def _check_ta_alias(cls, v: str) -> str:
        try:
            check_is_left_right_dot(v)
        except ValueError as e:
            raise ValueError(f"TaAlias failed LeftRightDot format validation: {e}")
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
        Axiom 1: Scada is SignedProof signer.
        Axiom 1: Scada is SignedProof signer.
        There is a ScadaCert created by the Gnf with this ta_alias, and  the txn is the OptIn.
        """
        # TODO: Implement check for axiom 1"
        return v

    def as_dict(self) -> Dict[str, Any]:
        d = self.dict()
        return d

    def as_type(self) -> str:
        return json.dumps(self.as_dict())

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class ScadaCertTransfer_Maker:
    type_name = "scada.cert.transfer"
    version = "000"

    def __init__(self, ta_alias: str, signed_proof: str):
        self.tuple = ScadaCertTransfer(
            TaAlias=ta_alias,
            SignedProof=signed_proof,
            #
        )

    @classmethod
    def tuple_to_type(cls, tuple: ScadaCertTransfer) -> str:
        """
        Given a Python class object, returns the serialized JSON type object
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: str) -> ScadaCertTransfer:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> ScadaCertTransfer:
        d2 = dict(d)
        if "TaAlias" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TaAlias")
        if "SignedProof" not in d2.keys():
            raise SchemaError(f"dict {d2} missing SignedProof")
        if "TypeName" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TypeName")

        return ScadaCertTransfer(
            TaAlias=d2["TaAlias"],
            SignedProof=d2["SignedProof"],
            TypeName=d2["TypeName"],
            Version="000",
        )
