"""Type atn.bid, version 001"""
import json
from enum import auto
from typing import Any
from typing import Dict
from typing import List
from typing import Literal

from fastapi_utils.enums import StrEnum
from gridworks.errors import SchemaError
from gridworks.message import as_enum
from pydantic import BaseModel
from pydantic import Field
from pydantic import root_validator
from pydantic import validator

from gwatn.enums import MarketPriceUnit
from gwatn.enums import MarketQuantityUnit
from gwatn.enums import MarketTypeName
from gwatn.types.price_quantity_unitless import PriceQuantityUnitless
from gwatn.types.price_quantity_unitless import PriceQuantityUnitless_Maker


class MarketPriceUnit000SchemaEnum:
    enum_name: str = "market.price.unit.000"
    symbols: List[str] = [
        "00000000",
    ]

    @classmethod
    def is_symbol(cls, candidate: str) -> bool:
        if candidate in cls.symbols:
            return True
        return False


class MarketPriceUnit000(StrEnum):
    USDPerMWh = auto()

    @classmethod
    def default(cls) -> "MarketPriceUnit000":
        return cls.USDPerMWh

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]


class MarketPriceUnitMap:
    @classmethod
    def type_to_local(cls, symbol: str) -> MarketPriceUnit:
        if not MarketPriceUnit000SchemaEnum.is_symbol(symbol):
            raise SchemaError(f"{symbol} must belong to MarketPriceUnit000 symbols")
        versioned_enum = cls.type_to_versioned_enum_dict[symbol]
        return as_enum(versioned_enum, MarketPriceUnit, MarketPriceUnit.default())

    @classmethod
    def local_to_type(cls, market_price_unit: MarketPriceUnit) -> str:
        if not isinstance(market_price_unit, MarketPriceUnit):
            raise SchemaError(f"{market_price_unit} must be of type {MarketPriceUnit}")
        versioned_enum = as_enum(
            market_price_unit, MarketPriceUnit000, MarketPriceUnit000.default()
        )
        return cls.versioned_enum_to_type_dict[versioned_enum]

    type_to_versioned_enum_dict: Dict[str, MarketPriceUnit000] = {
        "00000000": MarketPriceUnit000.USDPerMWh,
    }

    versioned_enum_to_type_dict: Dict[MarketPriceUnit000, str] = {
        MarketPriceUnit000.USDPerMWh: "00000000",
    }


class MarketTypeName000SchemaEnum:
    enum_name: str = "market.type.name.000"
    symbols: List[str] = [
        "00000000",
        "d20b81e4",
        "b36cbfb4",
        "94a3fe9b",
        "5f335bdb",
        "01a84101",
        "e997ccfb",
        "618f9c0a",
    ]

    @classmethod
    def is_symbol(cls, candidate: str) -> bool:
        if candidate in cls.symbols:
            return True
        return False


class MarketTypeName000(StrEnum):
    unknown = auto()
    rt5gate5 = auto()
    rt60gate5 = auto()
    da60 = auto()
    rt60gate30 = auto()
    rt15gate5 = auto()
    rt30gate5 = auto()
    rt60gate30b = auto()

    @classmethod
    def default(cls) -> "MarketTypeName000":
        return cls.unknown

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]


class MarketTypeNameMap:
    @classmethod
    def type_to_local(cls, symbol: str) -> MarketTypeName:
        if not MarketTypeName000SchemaEnum.is_symbol(symbol):
            raise SchemaError(f"{symbol} must belong to MarketTypeName000 symbols")
        versioned_enum = cls.type_to_versioned_enum_dict[symbol]
        return as_enum(versioned_enum, MarketTypeName, MarketTypeName.default())

    @classmethod
    def local_to_type(cls, market_type_name: MarketTypeName) -> str:
        if not isinstance(market_type_name, MarketTypeName):
            raise SchemaError(f"{market_type_name} must be of type {MarketTypeName}")
        versioned_enum = as_enum(
            market_type_name, MarketTypeName000, MarketTypeName000.default()
        )
        return cls.versioned_enum_to_type_dict[versioned_enum]

    type_to_versioned_enum_dict: Dict[str, MarketTypeName000] = {
        "00000000": MarketTypeName000.unknown,
        "d20b81e4": MarketTypeName000.rt5gate5,
        "b36cbfb4": MarketTypeName000.rt60gate5,
        "94a3fe9b": MarketTypeName000.da60,
        "5f335bdb": MarketTypeName000.rt60gate30,
        "01a84101": MarketTypeName000.rt15gate5,
        "e997ccfb": MarketTypeName000.rt30gate5,
        "618f9c0a": MarketTypeName000.rt60gate30b,
    }

    versioned_enum_to_type_dict: Dict[MarketTypeName000, str] = {
        MarketTypeName000.unknown: "00000000",
        MarketTypeName000.rt5gate5: "d20b81e4",
        MarketTypeName000.rt60gate5: "b36cbfb4",
        MarketTypeName000.da60: "94a3fe9b",
        MarketTypeName000.rt60gate30: "5f335bdb",
        MarketTypeName000.rt15gate5: "01a84101",
        MarketTypeName000.rt30gate5: "e997ccfb",
        MarketTypeName000.rt60gate30b: "618f9c0a",
    }


class MarketQuantityUnit000SchemaEnum:
    enum_name: str = "market.quantity.unit.000"
    symbols: List[str] = [
        "00000000",
        "c272f3b3",
    ]

    @classmethod
    def is_symbol(cls, candidate: str) -> bool:
        if candidate in cls.symbols:
            return True
        return False


class MarketQuantityUnit000(StrEnum):
    AvgMW = auto()
    AvgkW = auto()

    @classmethod
    def default(cls) -> "MarketQuantityUnit000":
        return cls.AvgMW

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]


class MarketQuantityUnitMap:
    @classmethod
    def type_to_local(cls, symbol: str) -> MarketQuantityUnit:
        if not MarketQuantityUnit000SchemaEnum.is_symbol(symbol):
            raise SchemaError(f"{symbol} must belong to MarketQuantityUnit000 symbols")
        versioned_enum = cls.type_to_versioned_enum_dict[symbol]
        return as_enum(versioned_enum, MarketQuantityUnit, MarketQuantityUnit.default())

    @classmethod
    def local_to_type(cls, market_quantity_unit: MarketQuantityUnit) -> str:
        if not isinstance(market_quantity_unit, MarketQuantityUnit):
            raise SchemaError(
                f"{market_quantity_unit} must be of type {MarketQuantityUnit}"
            )
        versioned_enum = as_enum(
            market_quantity_unit, MarketQuantityUnit000, MarketQuantityUnit000.default()
        )
        return cls.versioned_enum_to_type_dict[versioned_enum]

    type_to_versioned_enum_dict: Dict[str, MarketQuantityUnit000] = {
        "00000000": MarketQuantityUnit000.AvgMW,
        "c272f3b3": MarketQuantityUnit000.AvgkW,
    }

    versioned_enum_to_type_dict: Dict[MarketQuantityUnit000, str] = {
        MarketQuantityUnit000.AvgMW: "00000000",
        MarketQuantityUnit000.AvgkW: "c272f3b3",
    }


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


def check_is_market_type_name_lrd_format(v: str) -> None:
    from gwatn.enums import MarketTypeName

    try:
        x = v.split(".")
    except AttributeError:
        raise ValueError(f"{v} failed to split on '.'")
    if not x[0] in MarketTypeName.values():
        raise ValueError(f"{v} not recognized MarketType")
    g_node_alias = ".".join(x[1:])
    check_is_left_right_dot(g_node_alias)


def check_is_market_slot_name_lrd_format(v: str) -> None:
    """
    MaketSlotNameLrdFormat: the format of a MarketSlotName.
      - The first word must be a MarketTypeName
      - The last word (unix time of market slot start) must
      be a 10-digit integer divisible by 300 (i.e. all MarketSlots
      start at the top of 5 minutes)
      - More strictly, the last word must be the start of a
      MarketSlot for that MarketType (i.e. divisible by 3600
      for hourly markets)
      - The middle words have LeftRightDot format (GNodeAlias
      of the MarketMaker)
    Example: rt60gate5.d1.isone.ver.keene.1673539200

    """
    from gwatn.data_classes import MarketType

    try:
        x = v.split(".")
    except AttributeError:
        raise ValueError(f"{v} failed to split on '.'")
    slot_start = x[-1]
    if len(slot_start) != 10:
        raise ValueError(f"slot start {slot_start} not of length 10")
    try:
        slot_start = int(slot_start)
    except ValueError:
        raise ValueError(f"slot start {slot_start} not an int")
    if slot_start % 300 != 0:
        raise ValueError(f"slot start {slot_start} not a multiple of 300")

    market_type_name_lrd = ".".join(x[:-1])
    try:
        check_is_market_type_name_lrd_format(market_type_name_lrd)
    except ValueError as e:
        raise ValueError(f"e")

    market_type = MarketType.by_id[market_type_name_lrd.split(".")[0]]
    if not slot_start % (market_type.duration_minutes * 60) == 0:
        raise ValueError(
            f"market_slot_start_s mod {(market_type.duration_minutes * 60)} must be 0"
        )


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


class AtnBid(BaseModel):
    """AtomicTNode bid sent to a MarketMaker
    [More info](https://gridworks.readthedocs.io/en/latest/market-bid.html).
    """

    BidderAlias: str = Field(
        title="BidderAlias",
    )
    BidderGNodeInstanceId: str = Field(
        title="BidderGNodeInstanceId",
    )
    MarketSlotName: str = Field(
        title="MarketSlotName",
    )
    PqPairs: List[PriceQuantityUnitless] = Field(
        title="Price Quantity Pairs",
        description="The list of Price Quantity Pairs making up the bid. The units are provided by the AtnBid.PriceUnit and AtnBid.QuantityUnit.",
    )
    InjectionIsPositive: bool = Field(
        title="InjectionIsPositive",
        default=False,
    )
    PriceUnit: MarketPriceUnit = Field(
        title="PriceUnit",
        default=MarketPriceUnit.USDPerMWh,
    )
    QuantityUnit: MarketQuantityUnit = Field(
        title="QuantityUnit",
        default=MarketQuantityUnit.AvgMW,
    )
    SignedMarketFeeTxn: str = Field(
        title="SignedMarketFeeTxn",
    )
    TypeName: Literal["atn.bid"] = "atn.bid"
    Version: str = "001"

    @validator("BidderAlias")
    def _check_bidder_alias(cls, v: str) -> str:
        try:
            check_is_left_right_dot(v)
        except ValueError as e:
            raise ValueError(f"BidderAlias failed LeftRightDot format validation: {e}")
        return v

    @validator("BidderGNodeInstanceId")
    def _check_bidder_g_node_instance_id(cls, v: str) -> str:
        try:
            check_is_uuid_canonical_textual(v)
        except ValueError as e:
            raise ValueError(
                f"BidderGNodeInstanceId failed UuidCanonicalTextual format validation: {e}"
            )
        return v

    @validator("MarketSlotName")
    def _check_market_slot_name(cls, v: str) -> str:
        try:
            check_is_market_slot_name_lrd_format(v)
        except ValueError as e:
            raise ValueError(
                f"MarketSlotName failed MarketSlotNameLrdFormat format validation: {e}"
            )
        return v

    @validator("PqPairs")
    def _check_pq_pairs(cls, v: List) -> List:
        for elt in v:
            if not isinstance(elt, PriceQuantityUnitless):
                raise ValueError(
                    f"elt {elt} of PqPairs must have type PriceQuantityUnitless."
                )
        return v

    @validator("PriceUnit")
    def _check_price_unit(cls, v: MarketPriceUnit) -> MarketPriceUnit:
        return as_enum(v, MarketPriceUnit, MarketPriceUnit.USDPerMWh)

    @validator("QuantityUnit")
    def _check_quantity_unit(cls, v: MarketQuantityUnit) -> MarketQuantityUnit:
        return as_enum(v, MarketQuantityUnit, MarketQuantityUnit.AvgMW)

    @validator("SignedMarketFeeTxn")
    def _check_signed_market_fee_txn(cls, v: str) -> str:
        try:
            check_is_algo_msg_pack_encoded(v)
        except ValueError as e:
            raise ValueError(
                f"SignedMarketFeeTxn failed AlgoMsgPackEncoded format validation: {e}"
            )
        return v

    @root_validator
    def check_axiom_1(cls, v: dict) -> dict:
        """
        Axiom 1: PqPairs PriceMax matches MarketType.
        There is a GridWorks global list of MarketTypes (a GridWorks type), identified by their MarketTypeNames (a GridWorks enum).  The MarketType has a PriceMax, which must be the first price of the first PriceQuantity pair in PqPairs.
        """
        # TODO: Implement check for axiom 1"
        return v

    @root_validator
    def check_axiom_2(cls, v: dict) -> dict:
        """
        Axiom 2: .

        """
        # TODO: Implement check for axiom 2"
        return v

    def as_dict(self) -> Dict[str, Any]:
        d = self.dict()

        # Recursively call as_dict() for the SubTypes
        pq_pairs = []
        for elt in self.PqPairs:
            pq_pairs.append(elt.as_dict())
        d["PqPairs"] = pq_pairs
        del d["PriceUnit"]
        PriceUnit = as_enum(self.PriceUnit, MarketPriceUnit, MarketPriceUnit.default())
        d["PriceUnitGtEnumSymbol"] = MarketPriceUnitMap.local_to_type(PriceUnit)
        del d["QuantityUnit"]
        QuantityUnit = as_enum(
            self.QuantityUnit, MarketQuantityUnit, MarketQuantityUnit.default()
        )
        d["QuantityUnitGtEnumSymbol"] = MarketQuantityUnitMap.local_to_type(
            QuantityUnit
        )
        return d

    def as_type(self) -> str:
        return json.dumps(self.as_dict())

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class AtnBid_Maker:
    type_name = "atn.bid"
    version = "001"

    def __init__(
        self,
        bidder_alias: str,
        bidder_g_node_instance_id: str,
        market_slot_name: str,
        pq_pairs: List[PriceQuantityUnitless],
        injection_is_positive: bool,
        price_unit: MarketPriceUnit,
        quantity_unit: MarketQuantityUnit,
        signed_market_fee_txn: str,
    ):
        self.tuple = AtnBid(
            BidderAlias=bidder_alias,
            BidderGNodeInstanceId=bidder_g_node_instance_id,
            MarketSlotName=market_slot_name,
            PqPairs=pq_pairs,
            InjectionIsPositive=injection_is_positive,
            PriceUnit=price_unit,
            QuantityUnit=quantity_unit,
            SignedMarketFeeTxn=signed_market_fee_txn,
            #
        )

    @classmethod
    def tuple_to_type(cls, tuple: AtnBid) -> str:
        """
        Given a Python class object, returns the serialized JSON type object
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: str) -> AtnBid:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> AtnBid:
        d2 = dict(d)
        if "BidderAlias" not in d2.keys():
            raise SchemaError(f"dict {d2} missing BidderAlias")
        if "BidderGNodeInstanceId" not in d2.keys():
            raise SchemaError(f"dict {d2} missing BidderGNodeInstanceId")
        if "MarketSlotName" not in d2.keys():
            raise SchemaError(f"dict {d2} missing MarketSlotName")
        if "PqPairs" not in d2.keys():
            raise SchemaError(f"dict {d2} missing PqPairs")
        pq_pairs = []
        if not isinstance(d2["PqPairs"], List):
            raise SchemaError("PqPairs must be a List!")
        for elt in d2["PqPairs"]:
            if not isinstance(elt, dict):
                raise SchemaError(
                    f"elt {elt} of PqPairs must be "
                    "PriceQuantityUnitless but not even a dict!"
                )
            pq_pairs.append(PriceQuantityUnitless_Maker.dict_to_tuple(elt))
        d2["PqPairs"] = pq_pairs
        if "InjectionIsPositive" not in d2.keys():
            raise SchemaError(f"dict {d2} missing InjectionIsPositive")
        if "PriceUnitGtEnumSymbol" not in d2.keys():
            raise SchemaError(f"dict {d2} missing PriceUnitGtEnumSymbol")
        if d2["PriceUnitGtEnumSymbol"] in MarketPriceUnit000SchemaEnum.symbols:
            d2["PriceUnit"] = MarketPriceUnitMap.type_to_local(
                d2["PriceUnitGtEnumSymbol"]
            )
        else:
            d2["PriceUnit"] = MarketPriceUnit.default()
        if "QuantityUnitGtEnumSymbol" not in d2.keys():
            raise SchemaError(f"dict {d2} missing QuantityUnitGtEnumSymbol")
        if d2["QuantityUnitGtEnumSymbol"] in MarketQuantityUnit000SchemaEnum.symbols:
            d2["QuantityUnit"] = MarketQuantityUnitMap.type_to_local(
                d2["QuantityUnitGtEnumSymbol"]
            )
        else:
            d2["QuantityUnit"] = MarketQuantityUnit.default()
        if "SignedMarketFeeTxn" not in d2.keys():
            raise SchemaError(f"dict {d2} missing SignedMarketFeeTxn")
        if "TypeName" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TypeName")

        return AtnBid(
            BidderAlias=d2["BidderAlias"],
            BidderGNodeInstanceId=d2["BidderGNodeInstanceId"],
            MarketSlotName=d2["MarketSlotName"],
            PqPairs=d2["PqPairs"],
            InjectionIsPositive=d2["InjectionIsPositive"],
            PriceUnit=d2["PriceUnit"],
            QuantityUnit=d2["QuantityUnit"],
            SignedMarketFeeTxn=d2["SignedMarketFeeTxn"],
            TypeName=d2["TypeName"],
            Version="001",
        )
