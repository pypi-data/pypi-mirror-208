from pydantic import BaseModel

from gwatn import property_format
from gwatn.data_classes import MarketType
from gwatn.enums import MarketTypeName
from gwatn.types import MarketSlot
from gwatn.types import MarketTypeGt_Maker


DUMMY_ALGO_TXN = "gqNzaWfEQNPXbrAiWd+cNgsIaM3N0PSu3repauvmjuHmoKjh6sd3L5U4/YpovcXN7/ATH1LgcI4cgV+SU3VQ6bsm/gfAOQyjdHhuiaNhbXTNB9CjZmVlzQPoomZ2HaNnZW6qc2FuZG5ldC12MaJnaMQgaJXPYTdWaeTNSs8FMMzPNfV7SrHXqJgFsJLxRbSPjzCibHbNBAWjcmN2xCBWkH3PValty0Rb0cyZo69Alhp4IbNKFnhXtgJ++A9EzKNzbmTEIOJPEbccL6IqmeBeaLzbLav25U9jBMjloaIyF1eY9HFxpHR5cGWjcGF5"


class DijkstraChoice(BaseModel):
    PowerImportedKw: float
    NextNodeCostDollars: float


class CostAndQuantityBought(BaseModel):
    QuantityBought: float
    Cost: float


def name_from_market_slot(slot: MarketSlot) -> str:
    return f"{slot.Type.Name.value}.{slot.MarketMakerAlias}.{slot.StartUnixS}"


def market_slot_from_name(market_slot_name: str) -> MarketSlot:
    """rt60gate30b.d1.isone.ver.keene.1577836800"""
    try:
        property_format.check_is_market_slot_name_lrd_format(market_slot_name)
    except ValueError as e:
        raise Exception(
            f"market slot alias {market_slot_name} does not have market"
            " slot alias lrd format!"
        )
    words = market_slot_name.split(".")
    market_type_name = MarketTypeName(words[0])
    market_type_dc = MarketType.by_id[market_type_name]
    market_type = MarketTypeGt_Maker.dc_to_tuple(market_type_dc)
    market_maker_alias = ".".join(words[1:-1])
    slot_start = int(words[-1])
    return MarketSlot(
        Type=market_type, MarketMakerAlias=market_maker_alias, StartUnixS=slot_start
    )
