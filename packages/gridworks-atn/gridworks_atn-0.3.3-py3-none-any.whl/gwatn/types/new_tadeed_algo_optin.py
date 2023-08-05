"""Type new.tadeed.algo.optin, version 000"""
import json
from typing import Any
from typing import Dict
from typing import Literal

from gridworks.errors import SchemaError
from pydantic import BaseModel
from pydantic import Field
from pydantic import validator


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


class NewTadeedAlgoOptin(BaseModel):
    """ """

    NewTaDeedIdx: int = Field(
        title="NewTaDeedIdx",
    )
    OldTaDeedIdx: int = Field(
        title="OldTaDeedIdx",
    )
    TaDaemonAddr: str = Field(
        title="TaDaemonAddr",
    )
    ValidatorAddr: str = Field(
        title="ValidatorAddr",
    )
    SignedTaDeedCreationTxn: str = Field(
        title="SignedTaDeedCreationTxn",
    )
    TypeName: Literal["new.tadeed.algo.optin"] = "new.tadeed.algo.optin"
    Version: str = "000"

    @validator("TaDaemonAddr")
    def _check_ta_daemon_addr(cls, v: str) -> str:
        try:
            check_is_algo_address_string_format(v)
        except ValueError as e:
            raise ValueError(
                f"TaDaemonAddr failed AlgoAddressStringFormat format validation: {e}"
            )
        return v

    @validator("ValidatorAddr")
    def _check_validator_addr(cls, v: str) -> str:
        try:
            check_is_algo_address_string_format(v)
        except ValueError as e:
            raise ValueError(
                f"ValidatorAddr failed AlgoAddressStringFormat format validation: {e}"
            )
        return v

    @validator("SignedTaDeedCreationTxn")
    def _check_signed_ta_deed_creation_txn(cls, v: str) -> str:
        try:
            check_is_algo_msg_pack_encoded(v)
        except ValueError as e:
            raise ValueError(
                f"SignedTaDeedCreationTxn failed AlgoMsgPackEncoded format validation: {e}"
            )
        return v

    def as_dict(self) -> Dict[str, Any]:
        d = self.dict()
        return d

    def as_type(self) -> str:
        return json.dumps(self.as_dict())


class NewTadeedAlgoOptin_Maker:
    type_name = "new.tadeed.algo.optin"
    version = "000"

    def __init__(
        self,
        new_ta_deed_idx: int,
        old_ta_deed_idx: int,
        ta_daemon_addr: str,
        validator_addr: str,
        signed_ta_deed_creation_txn: str,
    ):
        self.tuple = NewTadeedAlgoOptin(
            NewTaDeedIdx=new_ta_deed_idx,
            OldTaDeedIdx=old_ta_deed_idx,
            TaDaemonAddr=ta_daemon_addr,
            ValidatorAddr=validator_addr,
            SignedTaDeedCreationTxn=signed_ta_deed_creation_txn,
            #
        )

    @classmethod
    def tuple_to_type(cls, tuple: NewTadeedAlgoOptin) -> str:
        """
        Given a Python class object, returns the serialized JSON type object
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: str) -> NewTadeedAlgoOptin:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> NewTadeedAlgoOptin:
        d2 = dict(d)
        if "NewTaDeedIdx" not in d2.keys():
            raise SchemaError(f"dict {d2} missing NewTaDeedIdx")
        if "OldTaDeedIdx" not in d2.keys():
            raise SchemaError(f"dict {d2} missing OldTaDeedIdx")
        if "TaDaemonAddr" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TaDaemonAddr")
        if "ValidatorAddr" not in d2.keys():
            raise SchemaError(f"dict {d2} missing ValidatorAddr")
        if "SignedTaDeedCreationTxn" not in d2.keys():
            raise SchemaError(f"dict {d2} missing SignedTaDeedCreationTxn")
        if "TypeName" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TypeName")

        return NewTadeedAlgoOptin(
            NewTaDeedIdx=d2["NewTaDeedIdx"],
            OldTaDeedIdx=d2["OldTaDeedIdx"],
            TaDaemonAddr=d2["TaDaemonAddr"],
            ValidatorAddr=d2["ValidatorAddr"],
            SignedTaDeedCreationTxn=d2["SignedTaDeedCreationTxn"],
            TypeName=d2["TypeName"],
            Version="000",
        )
