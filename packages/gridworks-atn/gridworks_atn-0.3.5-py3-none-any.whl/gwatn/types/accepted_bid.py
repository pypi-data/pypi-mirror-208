"""Type accepted.bid, version 000"""
import json
from typing import Any
from typing import Dict
from typing import List
from typing import Literal

from gridworks.errors import SchemaError
from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from gwatn.types.price_quantity_unitless import PriceQuantityUnitless
from gwatn.types.price_quantity_unitless import PriceQuantityUnitless_Maker


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


class AcceptedBid(BaseModel):
    """Bid acceptance sent from MarketMaker to a market partipant.

    This is a legally binding contract for the bidder to consume or produce the quantity
    in its Bid consistent with the actual price.
    [More info](https://gridworks.readthedocs.io/en/latest/market-bid.html).
    """

    MarketSlotName: str = Field(
        title="MarketSlotName",
    )
    BidderAlias: str = Field(
        title="BidderAlias",
    )
    PqPairs: List[PriceQuantityUnitless] = Field(
        title="PqPairs",
    )
    ReceivedTimeUnixNs: int = Field(
        title="ReceivedTimeUnixNs",
    )
    TypeName: Literal["accepted.bid"] = "accepted.bid"
    Version: str = "000"

    @validator("MarketSlotName")
    def _check_market_slot_name(cls, v: str) -> str:
        try:
            check_is_market_slot_name_lrd_format(v)
        except ValueError as e:
            raise ValueError(
                f"MarketSlotName failed MarketSlotNameLrdFormat format validation: {e}"
            )
        return v

    @validator("BidderAlias")
    def _check_bidder_alias(cls, v: str) -> str:
        try:
            check_is_left_right_dot(v)
        except ValueError as e:
            raise ValueError(f"BidderAlias failed LeftRightDot format validation: {e}")
        return v

    @validator("PqPairs")
    def _check_pq_pairs(cls, v: List) -> List:
        for elt in v:
            if not isinstance(elt, PriceQuantityUnitless):
                raise ValueError(
                    f"elt {elt} of PqPairs must have type PriceQuantityUnitless."
                )
        return v

    def as_dict(self) -> Dict[str, Any]:
        d = self.dict()

        # Recursively call as_dict() for the SubTypes
        pq_pairs = []
        for elt in self.PqPairs:
            pq_pairs.append(elt.as_dict())
        d["PqPairs"] = pq_pairs
        return d

    def as_type(self) -> str:
        return json.dumps(self.as_dict())

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class AcceptedBid_Maker:
    type_name = "accepted.bid"
    version = "000"

    def __init__(
        self,
        market_slot_name: str,
        bidder_alias: str,
        pq_pairs: List[PriceQuantityUnitless],
        received_time_unix_ns: int,
    ):
        self.tuple = AcceptedBid(
            MarketSlotName=market_slot_name,
            BidderAlias=bidder_alias,
            PqPairs=pq_pairs,
            ReceivedTimeUnixNs=received_time_unix_ns,
            #
        )

    @classmethod
    def tuple_to_type(cls, tuple: AcceptedBid) -> str:
        """
        Given a Python class object, returns the serialized JSON type object
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: str) -> AcceptedBid:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> AcceptedBid:
        d2 = dict(d)
        if "MarketSlotName" not in d2.keys():
            raise SchemaError(f"dict {d2} missing MarketSlotName")
        if "BidderAlias" not in d2.keys():
            raise SchemaError(f"dict {d2} missing BidderAlias")
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
        if "ReceivedTimeUnixNs" not in d2.keys():
            raise SchemaError(f"dict {d2} missing ReceivedTimeUnixNs")
        if "TypeName" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TypeName")

        return AcceptedBid(
            MarketSlotName=d2["MarketSlotName"],
            BidderAlias=d2["BidderAlias"],
            PqPairs=d2["PqPairs"],
            ReceivedTimeUnixNs=d2["ReceivedTimeUnixNs"],
            TypeName=d2["TypeName"],
            Version="000",
        )
