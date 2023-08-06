import csv
import json
import logging
import os
import uuid
from typing import List
from typing import Optional

import pendulum
from pydantic import BaseModel

import gwatn.atn_utils as atn_utils
import gwatn.brick_storage_heater.strategy_utils as strategy_utils
from gwatn.brick_storage_heater.strategy_utils import SlotStuff
from gwatn.types import AtnBid
from gwatn.types import AtnParamsBrickstorageheater as AtnParams
from gwatn.types import AtnParamsReport_Maker
from gwatn.types import FloParamsBrickstorageheater as FloParams
from gwatn.types import MarketSlot
from gwatn.types.ps_distprices_gnode.csv_distp_sync.csv_distp_sync_1_0_0 import (
    Csv_Distp_Sync_1_0_0,
)
from gwatn.types.ps_electricityprices_gnode.csv_eprt_sync.csv_eprt_sync_1_0_0 import (
    Csv_Eprt_Sync_1_0_0,
)
from gwatn.types.ws_forecast_gnode.csv_weather_forecast_sync.csv_weather_forecast_sync_1_0_0 import (
    Csv_Weather_Forecast_Sync_1_0_0,
)


LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)

LOGGER.setLevel(logging.WARNING)
DATA_DIR = "input_data"
EVENTSTORE_DIR = f"{DATA_DIR}/eventstore"

ELEC_PRICE_FILE = "input_data/electicity_prices/isone/eprt__w.isone.stetson__2020.csv"
DIST_PRICE_FILE = "input_data/electricity_prices/isone/distp__w.isone.stetson__2020__gw.me.versant.a1.res.ets.csv"
WEATHER_PRICE_FILE = (
    "input_data/weather/us/me/temp__ws.us.me.millinocketairport__2020.csv"
)


class FileNameMeta(BaseModel):
    FromGNodeAlias: str
    TypeName: str
    UnixTimeMs: int
    FileName: str


def fn_from_file_name(file: str) -> Optional[FileNameMeta]:
    try:
        fn = FileNameMeta(
            FromGNodeAlias=file.split("-")[0].strip(),
            TypeName=file.split("-")[1].strip(),
            UnixTimeMs=int(file.split("-")[2].split(".")[0]),
            FileName=file,
        )
    except Exception:
        LOGGER.info(f"Ignoring incorectly formatted file {file}")
        return None
    return fn


def atn_params_from_alias(alias: str, now_ms: int) -> AtnParams:
    files = os.listdir(EVENTSTORE_DIR)
    fns: List[FileNameMeta] = []
    for file in files:
        fn = fn_from_file_name(file)
        if fn:
            fns.append(fn)
    mine: List[FileNameMeta] = list(filter(lambda x: x.FromGNodeAlias == alias, fns))
    mine = list(filter(lambda x: x.TypeName == AtnParamsReport_Maker.type_name, mine))
    mine = list(filter(lambda x: x.UnixTimeMs <= now_ms, mine))
    mine.sort(key=lambda x: x.UnixTimeMs, reverse=True)
    if len(mine) == 0:
        return strategy_utils.dummy_atn_params()
    file_name = mine[0].FileName
    with open(f"{EVENTSTORE_DIR}/{file_name}") as f:
        data = json.load(f)
    params_report = AtnParamsReport_Maker.dict_to_tuple(data)
    if params_report.GNodeAlias != alias:
        raise Exception(
            f"file {file_name} was for {params_report.GNodeAlias}",
            f"instead of {alias}",
        )
    return params_report.Params


def get_flo_params(
    atn_params: AtnParams,
    slot: MarketSlot,
    storage_idx=50,
) -> FloParams:
    alias = atn_params.GNodeAlias
    start_s = slot.StartUnixS
    slices = atn_params.FloSlices
    slice_duration_minutes = atn_params.SliceDurationMinutes

    DATA_DIR = "input_data"
    file_name = "heat_profile_data.csv"
    f"{DATA_DIR}/{file_name}"

    defaults = []
    with open(f"{DATA_DIR}/{file_name}") as f:
        reader = csv.reader(f)
        for row in reader:
            defaults.append(row)
    aliases: List[str] = defaults[10]
    try:
        idx: int = aliases.index(alias)
    except ValueError:
        LOGGER.warning(f"No heat profile data found for {alias}")
        return strategy_utils.dummy_flo_params()

    dt = pendulum.datetime(
        year=int(defaults[4][1]),
        month=int(defaults[5][1]),
        day=int(defaults[6][1]),
        hour=int(defaults[7][1]),
        minute=int(defaults[8][1]),
    )
    file_start = dt.int_timestamp
    if start_s < file_start:
        raise Exception(
            f"Tried to get flo params at {pendulum.from_timestamp(start_s)}. "
            f"Only have data starting at {pendulum.from_timestamp(file_start)}"
        )
    FIRST_HEAT_RATIO_IDX = 11
    start_idx = int((start_s - file_start) / 3600) + FIRST_HEAT_RATIO_IDX

    power_required_list: List[float] = []
    for i in range(slices):
        try:
            power_required = (
                float(defaults[start_idx + i][idx]) * atn_params.AnnualHvacKwhTh
            )
        except:
            fail_t = start_s + i * 3600
            raise Exception(f"No heat use data for {pendulum.from_timestamp(fail_t)}!")
        power_required_list.append(power_required)

    ep = Csv_Eprt_Sync_1_0_0(ELEC_PRICE_FILE).payload
    ep_start = pendulum.datetime(
        year=ep.StartYearUtc,
        month=ep.StartMonthUtc,
        day=ep.StartDayUtc,
        hour=ep.StartHourUtc,
        minute=ep.StartMinuteUtc,
    ).int_timestamp
    start_idx = int((start_s - ep_start) / 3600)
    elec_price_list: List[float] = ep.Prices[start_idx : start_idx + slices]

    dp = Csv_Distp_Sync_1_0_0(DIST_PRICE_FILE).payload
    dp_start = pendulum.datetime(
        year=dp.StartYearUtc,
        month=dp.StartMonthUtc,
        day=dp.StartDayUtc,
        hour=dp.StartHourUtc,
        minute=dp.StartMinuteUtc,
    ).int_timestamp
    start_idx = int((start_s - dp_start) / 3600)
    dist_price_list: List[float] = dp.Prices[start_idx : start_idx + slices]

    tp = Csv_Weather_Forecast_Sync_1_0_0(WEATHER_PRICE_FILE).payload
    tp_start = pendulum.datetime(
        year=tp.StartYearUtc,
        month=tp.StartMonthUtc,
        day=tp.StartDayUtc,
        hour=tp.StartHourUtc,
    ).int_timestamp
    start_idx = int((start_s - tp_start) / 3600)
    temp_list: List[float] = tp.Temperatures[start_idx : start_idx + slices]

    start = pendulum.from_timestamp(start_s)
    d = dict(atn_params.dict(), TypeName="flo.params.brickstorageheater", Version="000")
    d["IsRegulating"] = False
    d["SliceDurationMinutes"] = [slice_duration_minutes] * slices
    d["PowerRequiredByHouseFromSystemAvgKwList"] = power_required_list
    d["OutsideTempF"] = temp_list
    d["RealtimeElectricityPrice"] = elec_price_list
    d["DistributionPrice"] = dist_price_list
    d["RegulationPrice"] = []
    d["RtElecPriceUid"] = str(uuid.uuid4())
    d["WeatherUid"] = str(uuid.uuid4())
    d["DistPriceUid"] = str(uuid.uuid4())
    d["StartYearUtc"] = start.year
    d["StartMonthUtc"] = start.month
    d["StartDayUtc"] = start.day
    d["StartHourUtc"] = start.hour
    d["StartMinuteUtc"] = start.minute
    d["StartingIdx"] = storage_idx

    return FloParams(**d)


def initialize_slot_stuff(
    slot: MarketSlot, atn_params: AtnParams, atn_gni_id: str
) -> SlotStuff:
    flo_params = get_flo_params(atn_params=atn_params, slot=slot, storage_idx=0)

    bid = AtnBid(
        BidderAlias=atn_params.GNodeAlias,
        BidderGNodeInstanceId=atn_gni_id,
        MarketSlotName=atn_utils.name_from_market_slot(slot),
        BidList=[],
        InjectionIsPositive=False,
        PriceUnit=slot.Type.PriceUnit,
        QuantityUnit=slot.Type.QuantityUnit,
        SignedMarketFeeTxn=atn_utils.DUMMY_ALGO_TXN,
    )
    return SlotStuff(Slot=slot, BidParams=flo_params, Bid=bid)
