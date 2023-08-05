from typing import Optional

from pydantic import BaseModel

from gwatn.brick_storage_heater.flo import Flo__BrickStorageHeater as Flo
from gwatn.types import AtnBid
from gwatn.types import AtnParamsBrickstorageheater as AtnParams
from gwatn.types import FloParamsBrickstorageheater as FloParams
from gwatn.types import MarketSlot


class SlotStuff(BaseModel):
    Slot: MarketSlot
    BidParams: Optional[FloParams] = None
    Flo: Optional[Flo] = None
    Bid: Optional[AtnBid] = None
    Price: Optional[float] = None


def dummy_bid() -> AtnBid:
    return AtnBid(
        BidderAlias="d1.isone.dummy.ta",
    )


def dummy_slot_stuff(slot: MarketSlot) -> SlotStuff:
    return SlotStuff(
        Slot=slot, FloStartIdx=50, BidParams=dummy_flo_params(), AtnBid=dummy_bid()
    )


def is_dummy_slot_stuff(bid_stuff: SlotStuff) -> bool:
    if is_dummy_flo_params(bid_stuff.BidParams):
        return True
    return False


def is_dummy_atn_params(atn_params: AtnParams) -> bool:
    if atn_params.GNodeAlias == "d1.isone.dummy.ta":
        return True
    return False


def dummy_atn_params() -> AtnParams:
    return AtnParams(
        SliceDurationMinutes=60,
        FloSlices=48,
        GNodeAlias="d1.isone.dummy.ta",
        GNodeInstanceId="00000000-0000-0000-0000-000000000000",
        TypeName="atn.params.heatpumpwithbooststore",
        Version="000",
    )


def is_dummy_flo_params(flo_params: FloParams) -> bool:
    if flo_params.RtElecPriceUid == "00000000-0000-0000-0000-000000000000":
        return True
    return False


def dummy_flo_params() -> FloParams:
    return FloParams(
        RtElecPriceUid="00000000-0000-0000-0000-000000000000",
        WeatherUid="00000000-0000-0000-0000-000000000000",
    )


def get_max_store_kwh_th(params: FloParams) -> float:
    """Use max store temp, room temp, and CF to get max store energy in kWh_th"""
    room_temp_c = (params.RoomTempF - 32) * 5 / 9
    return (params.MaxBrickTempC - room_temp_c) * params.C


def get_house_worst_case_heat_output_avg_kw(params: FloParams) -> float:
    design_t = params.HouseWorstCaseTempF
    this_run_t = min(params.OutsideTempF)
    room_t = params.RoomTempF
    p = params.PowerRequiredByHouseFromSystemAvgKwList
    this_run_max_system_kw = max(p)
    this_run_max_kw_in = this_run_max_system_kw + params.AmbientPowerInKw
    dd_max_kw_in = this_run_max_kw_in * (room_t - design_t) / (room_t - this_run_t)
    return dd_max_kw_in - params.AmbientPowerInKw
