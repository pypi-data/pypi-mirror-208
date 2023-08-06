""" BrickStorageHeater AtomicTNode Strategy.

 This is a heating and bidding strategy for a thermal storage heater that is
 designed to heat part or all of a single room. The storage medium is ceramic
 bricks and the heating source is resistive elements embedded in those bricks.

 This kind of heater is often called a Night Storage Heater in the UK, and
 is often also referred to (ambigiously, since there are other kinds) as
 an Electric Thermal Storage (ETS) heater.
 """
import functools
import logging
import math
import random
import time
import uuid
from typing import no_type_check

import dotenv
import gridworks.algo_utils as algo_utils
import pendulum
import requests
import satn.strategies.heatpumpwithbooststore.atn_utils as atn_utils
import satn.strategies.heatpumpwithbooststore.dev_io as dev_io
from algosdk import encoding
from algosdk.future import transaction
from algosdk.v2client.algod import AlgodClient
from gridworks.algo_utils import BasicAccount
from gridworks.utils import RestfulResponse
from satn.strategies.heatpumpwithbooststore.atn_utils import SlotStuff
from satn.strategies.heatpumpwithbooststore.edge import (
    Edge__SpaceHeat__Water_HeatPumpAndBoost__Alpha as Edge,
)
from satn.strategies.heatpumpwithbooststore.flo import (
    HeatPumpWithBoostStore__Flo as Flo,
)

import gwatn.config as config
from gwatn.atn_actor_base import AtnActorBase
from gwatn.data_classes.market_type import Rt60Gate30B
from gwatn.enums import GNodeRole
from gwatn.enums import MessageCategory
from gwatn.enums import MessageCategorySymbol
from gwatn.enums import UniverseType
from gwatn.types import AcceptedBid_Maker
from gwatn.types import AtnParamsBrickstorageheater as AtnParams
from gwatn.types import AtnParamsReport_Maker
from gwatn.types import HeartbeatA
from gwatn.types import HeartbeatA_Maker
from gwatn.types import LatestPrice
from gwatn.types import MarketSlot
from gwatn.types import MarketTypeGt
from gwatn.types import MarketTypeGt_Maker
from gwatn.types import PriceQuantityUnitless
from gwatn.types import Ready_Maker
from gwatn.types import SimplesimSnapshotBrickstorageheater_Maker as Snapshot_Maker
from gwatn.types import SimTimestep


LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)

LOGGER.setLevel(logging.WARNING)


class Atn__BrickStorageHeater(AtnActorBase):
    """AtomicTNode HeatPumpWithBoostStore strategy for thermal storage heat pump
    space heating system"""

    def __init__(
        self,
        settings: config.AtnSettings = config.AtnSettings(
            _env_file=dotenv.find_dotenv()
        ),
    ):
        super().__init__(settings)
        LOGGER.info("Initializing HeatPumpWithBoostStore Atn")
        self.algo_acct: BasicAccount = BasicAccount(settings.sk.get_secret_value())
        self.algo_client: AlgodClient = AlgodClient(
            settings.algo_api_secrets.algod_token.get_secret_value(),
            settings.public.algod_address,
        )
        self.atn_params: AtnParams = atn_utils.dummy_atn_params()
        self.market_type: MarketTypeGt = MarketTypeGt_Maker.dc_to_tuple(Rt60Gate30B)
        self.active_run: SlotStuff = atn_utils.dummy_slot_stuff(
            slot=self.active_slot(self.market_type)
        )
        self.next_run: SlotStuff = atn_utils.dummy_slot_stuff(
            slot=self.next_slot(self.market_type)
        )
        self.store_kwh: float = 0
        self.heatpump_kw: float = 0
        self.boost_kw: float = 0
        self.cop: float = 2.5
        self.store_update_time: float = self.time()
        self.latest_price_received_time: float = 0
        self.latest_price_dollars_per_mwh: float = 10**6
        self._first_start_finished: bool = False

    @no_type_check
    def strategy_rabbit_startup(self) -> None:
        mm_alias_lrh = self.settings.market_maker_alias.replace(".", "-")
        rjb = MessageCategorySymbol.rjb.value
        binding = f"{rjb}.{mm_alias_lrh}.marketmaker.latest-price.{self.market_type.Name.value}"
        cb = functools.partial(self.on_marketprice_bindok, binding=binding)
        self._consume_channel.queue_bind(
            self.queue_name, "marketmakermic_tx", routing_key=binding, callback=cb
        )

        pong = HeartbeatA_Maker(
            my_hex=str(random.choice("0123456789abcdef")), your_last_hex="0"
        ).tuple
        self.send_message(
            payload=pong,
            to_role=GNodeRole.Supervisor,
            to_g_node_alias=self.settings.my_super_alias,
        )
        d = pendulum.from_timestamp(time.time())
        LOGGER.warning(
            f"[{self.short_alias}] Sent first heartbeat to super: {d.minute}:{d.second}.{d.microsecond}"
        )

    @no_type_check
    def on_marketprice_bindok(self, _unused_frame, binding) -> None:
        LOGGER.info(f"Queue {self.queue_name} bound with {binding}")

    def heartbeat_received(self, from_alias: str, ping: HeartbeatA):
        pong = HeartbeatA_Maker(
            my_hex=str(random.choice("0123456789abcdef")), your_last_hex=ping.MyHex
        ).tuple

        self.send_message(
            payload=pong,
            to_role=GNodeRole.Supervisor,
            to_g_node_alias=self.settings.my_super_alias,
        )

        LOGGER.debug(
            f"[{self.short_alias}] Sent HB: SuHex {pong.YourLastHex}, AtnHex {pong.MyHex}"
        )

    def new_timestep(self, payload: SimTimestep) -> None:
        # LOGGER.info("----------------------------------------------------")
        # LOGGER.info(f"[{self.time_str()}: {self.short_alias}] NEW TIMESTEP")
        # LOGGER.info("----------------------------------------------------")

        # This gets called on the first timestep
        if atn_utils.is_dummy_atn_params(self.atn_params):
            self.get_initial_params()
            LOGGER.info("Correcting runs on initial timestep")
            self.active_run = atn_utils.dummy_slot_stuff(
                slot=self.last_slot(self.market_type),
            )
            try:
                self.next_run = dev_io.initialize_slot_stuff(
                    slot=self.active_slot(self.market_type),
                    atn_params=self.atn_params,
                )
            except Exception as e:
                LOGGER.warning(
                    f"Failed to initialize FloParams! Not creating a next_run {e}"
                )
                return

        try:
            self.update_store_level()
        except Exception:
            LOGGER.exception("Error in update_store_level")

        # Note: compressing the bid and the market start into the same time,
        # since time steps are only once per slot right now
        if self.time() >= self.next_run.Slot.StartUnixS:
            self.active_run = self.next_run
            self.active_run.BidParams.StartingStoreIdx = self.store_idx()
            try:
                self.get_bid()
            except Exception:
                LOGGER.exception("Error in get_bid")
            self.next_run = dev_io.initialize_slot_stuff(
                slot=self.next_slot(self.market_type),
                atn_params=self.atn_params,
            )
            try:
                self.submit_bid(self.active_run)
            except Exception:
                LOGGER.exception("Error in submit_bid")
        if self.active_run.Price is not None:
            self.respond_to_price()

    def repeat_timestep(self, payload: SimTimestep) -> None:
        LOGGER.info(f"[{self.time_str()}: {self.short_alias}] Timestep received again")

    def latest_price_from_market_maker(self, payload: LatestPrice) -> None:
        self.mm_payload = payload

        if payload.FromGNodeAlias != self.settings.market_maker_alias:
            LOGGER.warning(
                f"Received price from {payload.FromGNodeAlias}."
                f" Expected {self.settings.market_maker_alias} "
            )
            return
        slot = atn_utils.market_slot_from_name(payload.MarketSlotName)

        # time_str = pendulum.from_timestamp(slot.StartUnixS).strftime("%m/%d/%Y, %H:%M")
        # LOGGER.info("----------------------------------------------------")
        # LOGGER.info(
        #     f"[{self.time_str()}: {self.short_alias}] LATEST PRICE From MarketMaker: "
        #     f"${payload.PriceTimes1000 / 1000}/Mwh for slot starting {time_str}"
        # )
        # LOGGER.info("----------------------------------------------------")
        if slot.Type != self.market_type:
            LOGGER.warning(
                f"Received price for {slot.Type}, only participate in {self.market_type}"
            )
            return

        if slot == self.active_run.Slot:
            # LOGGER.info("Received price from MarketMaker. Adding price to active run")
            self.active_run.Price = payload.PriceTimes1000 / 1000
        elif slot == self.next_run.Slot:
            # this happens when the price arrives before the timestep
            # LOGGER.info("Received price from MarketMaker. Adding price to next run")
            self.next_run.Price = payload.PriceTimes1000 / 1000
        else:
            raise Exception("HUH. did not add price to a run")

        if self.active_run.Price is not None:
            self.respond_to_price()

    def respond_to_price(self) -> None:
        try:
            self.update_power_levels()
        except Exception:
            LOGGER.exception("Error in update_power_levels")
        payload = Snapshot_Maker(
            from_g_node_alias=self.alias,
            from_g_node_instance_id=self.g_node_instance_id,
            boost_power_kw_times1000=int(self.boost_kw * 1000),
            heatpump_power_kw_times1000=int(self.heatpump_kw * 1000),
            cop_times10=int(self.cop * 10),
            store_kwh=int(self.store_kwh),
            max_store_kwh=int(atn_utils.get_max_store_kwh_th(self.atn_params)),
            about_terminal_asset_alias=self.alias + ".ta",
        ).tuple
        # pprint(payload)
        self.send_message(
            payload=payload, message_category=MessageCategory.RabbitJsonBroadcast
        )

        payload = Ready_Maker(
            from_g_node_alias=self.alias,
            from_g_node_instance_id=self.g_node_instance_id,
            time_unix_s=int(self.time()),
        ).tuple
        self.send_message(
            payload=payload,
            to_role=GNodeRole.TimeCoordinator,
            to_g_node_alias=self.settings.time_coordinator_alias,
        )

    #########################
    # Terminal Asset State
    #########################

    def update_power_levels(self) -> None:
        # use price and Flo results to figure out heatpump and boost levels
        if self.active_run.Flo is None:
            return
        node = self.active_run.Flo.node[0][self.active_run.Flo.starting_store_idx]
        edge: Edge = list(
            filter(
                lambda x: x.end_idx == node.best_next_idx,
                self.active_run.Flo.edges[node],
            )
        )[0]
        self.heatpump_kw = edge.hp_electricity_avg_kw
        self.boost_kw = edge.boost_electricity_used_avg_kw
        self.cop = self.active_run.Flo.cop[0]
        # LOGGER.info(
        #     f"[{self.time_str()}: {self.short_alias}] Updating state: heatpump {round(self.heatpump_kw,2)}"
        # )

    def update_store_level(self) -> None:
        if atn_utils.is_dummy_slot_stuff(self.active_run):
            LOGGER.info(f"Not updating storage - active run is a dummy")
            self.store_update_time = self.time()
            return
        duration_minutes = int((self.time() - self.store_update_time) / 60)
        if duration_minutes != self.market_type.DurationMinutes:
            raise Exception(
                f"In update_store_level: Expected {self.market_type.DurationMinutes} minutes, got {duration_minutes} minutes."
            )
        flo = self.active_run.Flo
        if flo is None:
            raise Exception(
                f"In update_store_level: Expected Flo for last_run {self.active_run}!"
            )
        # TODO: find next step in graph based on the Flo, the Bid, and the actual price
        if flo.starting_store_idx != self.store_idx():
            raise Exception(
                f"flo.starting_idx is {flo.starting_store_idx} but self.store_idx is {self.store_idx()}!"
            )
        try:
            store_idx = flo.node[0][flo.starting_store_idx].best_next_idx
        except:
            raise Exception(f"Flo node did not have best_node_idx!")
        # self.store_kwh = ...
        self.store_kwh = (
            store_idx
            * atn_utils.get_max_store_kwh_th(self.atn_params)
            / self.atn_params.StorageSteps
        )
        # LOGGER.info(
        #     f"[{self.time_str()}: {self.short_alias}] Storage level {round(self.store_kwh,2)} kWh, "
        #     f"StoreIdx {self.active_run.BidParams.StartingStoreIdx}"
        # )
        self.store_update_time = self.time()

    ########################
    # FLO
    ########################

    def get_bid(self):
        self.active_run.Flo = Flo(
            params=self.active_run.BidParams, d_graph_id=str(uuid.uuid4())
        )
        slot_start = self.active_run.Slot.StartUnixS
        time_str = pendulum.from_timestamp(slot_start).strftime("%m/%d/%Y, %H:%M")
        # LOGGER.info(f"[{self.time_str()}: {self.short_alias}] Solving Flo ")
        self.active_run.Flo.solve_dijkstra()
        # export_xlsx(alias=self.alias, flo=flo, atn_params=self.atn_params)
        node = self.active_run.Flo.node[0][self.active_run.Flo.starting_store_idx]
        edge: Edge = list(
            filter(
                lambda x: x.end_idx == node.best_next_idx,
                self.active_run.Flo.edges[node],
            )
        )[0]
        q = edge.hp_electricity_avg_kw + edge.boost_electricity_used_avg_kw
        pq = PriceQuantityUnitless(
            PriceTimes1000=int(
                self.active_run.Flo.params.RealtimeElectricityPrice[0] * 1000
            ),
            QuantityTimes1000=int(q * 1000),
        )
        bid_list = [pq]
        self.active_run.Bid.BidList = bid_list

    ########################
    # Market transactions
    ######################

    def pay_market_fee(self) -> str:
        market_fee_micro_algos = 2 * 10**3
        txn = transaction.PaymentTxn(
            sender=self.algo_acct.addr,
            receiver=self.settings.market_maker_algo_address,
            amt=market_fee_micro_algos,
            sp=self.algo_client.suggested_params(),
        )
        signed_txn = txn.sign(self.algo_acct.sk)
        try:
            self.algo_client.send_transaction(signed_txn)
        except Exception as e:
            note = f"Algorand Failure sending market payment transaction: {e}"
            LOGGER.info(note)
            return atn_utils.DUMMY_ALGO_TXN
        try:
            algo_utils.wait_for_transaction(self.algo_client, signed_txn.get_txid())
        except:
            return atn_utils.DUMMY_ALGO_TXN
        return encoding.msgpack_encode(signed_txn)

    def submit_bid(self, slot_stuff: SlotStuff) -> RestfulResponse:
        slot_stuff.Bid.SignedMarketFeeTxn = self.pay_market_fee()
        slot_start = slot_stuff.Slot.StartUnixS
        time_str = pendulum.from_timestamp(slot_start).strftime("%m/%d/%Y, %H:%M")
        # LOGGER.info(
        #     f"[{self.time_str()}: {self.short_alias}] Submitting bid to MarketMaker RestAPI for Slot starting {time_str}"
        # )

        api_endpoint = f"{self.settings.mm_api_root}/atn-bid/"
        r = requests.post(url=api_endpoint, json=slot_stuff.Bid.as_dict())

        # Duplicate on rabbit broker for ear
        self.send_message(
            payload=slot_stuff.Bid,
            to_role=GNodeRole.MarketMaker,
            to_g_node_alias=self.settings.market_maker_alias,
        )

        if r.status_code > 200:
            if r.status_code == 422:
                note = f"Error entering SLA: " + r.json()["detail"]
            else:
                note = r.reason
            return RestfulResponse(Note=note, HttpStatusCode=422)
        else:
            rr = RestfulResponse(**r.json())
            if rr.PayloadTypeName == AcceptedBid_Maker.type_name:
                ab = AcceptedBid_Maker.dict_to_tuple(rr.PayloadAsDict)
                self.send_message(
                    payload=ab, message_category=MessageCategory.RabbitJsonBroadcast
                )
            # pprint(rr)
            return rr

    ########################
    # Initialization
    ########################

    def dev_get_initial_params(self) -> None:
        if not atn_utils.is_dummy_atn_params(self.atn_params):
            LOGGER.warning("Tried to get initial params but already have them")

        now_ms = int(self.time()) * 1000
        self.atn_params = dev_io.atn_params_from_alias(alias=self.alias, now_ms=now_ms)
        self.atn_params.GNodeInstanceId = self.g_node_instance_id
        if atn_utils.is_dummy_atn_params(self.atn_params):
            LOGGER.warning(f"No atn_params for {self.alias} before {self.time_str()}")
            return
        payload = AtnParamsReport_Maker(
            g_node_alias=self.alias,
            g_node_instance_id=self.g_node_instance_id,
            time_unix_s=int(self.time()),
            atn_params=self.atn_params,
            irl_time_unix_s=int(time.time()),
        ).tuple

        self.send_message(
            payload=payload, message_category=MessageCategory.RabbitJsonBroadcast
        )
        # LOGGER.info(f"[{self.time_str()}: {self.short_alias}] Initial params loaded")
        # pprint(self.atn_params)

    def get_initial_params(self) -> None:
        if self.universe_type == UniverseType.Dev:
            self.dev_get_initial_params()
        else:
            raise NotImplementedError

    @property
    def short_alias(self) -> str:
        return self.alias.split(".")[-1]

    ##################
    # Market slot starts
    ##################

    def last_slot(self, market_type: MarketTypeGt) -> MarketSlot:
        start_s = self.active_slot(
            market_type
        ).StartUnixS - self.market_slot_duration_s(market_type)
        return MarketSlot(
            Type=market_type,
            MarketMakerAlias=self.active_slot(market_type).MarketMakerAlias,
            StartUnixS=start_s,
        )

    def active_slot(self, market_type: MarketTypeGt) -> MarketSlot:
        market_delta = market_type.DurationMinutes * 60
        start = math.floor(self.time() / market_delta) * market_delta
        return MarketSlot(
            Type=market_type,
            MarketMakerAlias=self.settings.market_maker_alias,
            StartUnixS=start,
        )

    def next_slot(self, market_type: MarketTypeGt) -> MarketSlot:
        start_s = self.active_slot(
            market_type
        ).StartUnixS + self.market_slot_duration_s(market_type)
        return MarketSlot(
            Type=market_type,
            MarketMakerAlias=self.active_slot(market_type).MarketMakerAlias,
            StartUnixS=start_s,
        )

    def market_slot_duration_s(self, market_type: MarketTypeGt) -> int:
        return market_type.DurationMinutes * 60

    #############
    # TerminalAsset properties
    #################

    def store_idx(self) -> int:
        return round(
            self.atn_params.StorageSteps
            * self.store_kwh
            / atn_utils.get_max_store_kwh_th(self.atn_params)
        )
