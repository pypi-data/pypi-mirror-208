""" AtnActorBase """
import functools
import logging
import random
import time
import uuid
from abc import abstractmethod
from typing import Optional
from typing import cast
from typing import no_type_check

import gridworks.algo_utils as algo_utils
import pendulum
from algosdk.atomic_transaction_composer import TransactionWithSigner
from algosdk.future.transaction import *
from algosdk.v2client.algod import AlgodClient
from beaker.client import ApplicationClient
from gridworks.algo_utils import BasicAccount
from gridworks.enums import GNodeRole
from gridworks.message import as_enum
from gwproto.message import Message as ScadaMessage
from gwproto.messages import Ack
from gwproto.messages import GtShStatusEvent
from gwproto.messages import PeerActiveEvent
from gwproto.messages import Ping as GridworksPing
from gwproto.messages import SnapshotSpaceheatEvent
from pydantic import BaseModel

from gwatn.config import AtnSettings
from gwatn.dispatch_contract import DispatchContract
from gwatn.enums import AlgoCertType
from gwatn.enums import MessageCategorySymbol
from gwatn.enums import UniverseType
from gwatn.two_channel_actor_base import TwoChannelActorBase
from gwatn.types import AtnParams
from gwatn.types import DispatchContractConfirmed_Maker
from gwatn.types import GtShStatus
from gwatn.types import GwCertId
from gwatn.types import GwCertId_Maker
from gwatn.types import HeartbeatA
from gwatn.types import HeartbeatA_Maker
from gwatn.types import HeartbeatB
from gwatn.types import HeartbeatB_Maker
from gwatn.types import JoinDispatchContract
from gwatn.types import JoinDispatchContract_Maker
from gwatn.types import LatestPrice
from gwatn.types import LatestPrice_Maker
from gwatn.types import PowerWatts
from gwatn.types import SimTimestep
from gwatn.types import SimTimestep_Maker
from gwatn.types import SnapshotSpaceheat


LOG_FORMAT = (
    "%(levelname) -10s %(sasctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)


class HbStatus(BaseModel):
    LastHeartbeatReceivedMs: int
    AtnLastHex: str = "0"
    ScadaLastHex: str = "0"
    # To see beaker issue an ABI complaint:
    # ScadaLastHex: Optional[str] = None
    #
    # This will create an HbStatus with ScadaLastHex of None
    # when the Atn is initialized.


def dummy_atn_params() -> AtnParams:
    return AtnParams(
        SliceDurationMinutes=60,
        FloSlices=48,
        GNodeAlias="d1.isone.dummy.ta",
        GNodeInstanceId="00000000-0000-0000-0000-000000000000",
        TypeName="atn.params.heatpumpwithbooststore",
        Version="000",
    )


class AtnActorBase(TwoChannelActorBase):
    def __init__(self, settings: AtnSettings, use_algo: bool = False):
        super().__init__(settings=settings)
        self.settings: AtnSettings = settings
        self.scada_gni_id = settings.scada_gni_id
        self._time: float = self.get_initial_time_s()

        if use_algo is True:
            self.acct: BasicAccount = BasicAccount(settings.sk.get_secret_value())
            self.client: AlgodClient = AlgodClient(
                settings.algo_api_secrets.algod_token.get_secret_value(),
                settings.public.algod_address,
            )
            if algo_utils.algos(self.acct.addr) < 5:
                raise Exception(
                    f"Insufficiently funded. Make sure atn has at least 5 algos"
                )
            # TODO: move this into spaceheat along with join_dispatch_contract_received
            self.atn_params: AtnParams = dummy_atn_params()
            self.sp = self.client.suggested_params()
            self.sp.flat_fee = True
            self.sp.fee = 2000
            # this is initialized with the AppId provided by the SCADA
            self.dc_app_id: Optional[int] = None
            self.dc_client: Optional[ApplicationClient] = None
            self.check_for_dispatch_contract()
            self.universe_type = as_enum(
                self.settings.universe_type_value, UniverseType, UniverseType.default()
            )
            self.trading_rights_id: Optional[GwCertId] = None
            self.update_trading_rights()
            self.hb_status = HbStatus(LastHeartbeatReceivedMs=int(time.time() * 1000))

    def local_rabbit_startup(self) -> None:
        rjb = MessageCategorySymbol.rjb.value
        tc_alias_lrh = self.settings.time_coordinator_alias.replace(".", "-")
        binding = f"{rjb}.{tc_alias_lrh}.timecoordinator.sim-timestep"

        cb = functools.partial(self.on_timecoordinator_bindok, binding=binding)
        self._consume_channel.queue_bind(
            self.queue_name, "timecoordinatormic_tx", routing_key=binding, callback=cb
        )
        LOGGER.info(
            f"Queue {self.queue_name} bound to timecoordinatormic_tx with {binding} "
        )
        scada_alias_lrh = self.scada_alias.replace(".", "-")
        binding = f"gw.{scada_alias_lrh}.#"
        cb = functools.partial(self.on_scada_bindok, binding=binding)
        self._consume_channel.queue_bind(
            self.queue_name, "amq.topic", routing_key=binding, callback=cb
        )
        LOGGER.info(f"Queue {self.queue_name} bound to amq.topic with {binding} ")
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
            f"[{self.alias}] Sent first heartbeat to super: {d.minute}:{d.second}.{d.microsecond}"
        )
        self.strategy_rabbit_startup()

    def strategy_rabbit_startup(self) -> None:
        pass

    @no_type_check
    def on_timecoordinator_bindok(self, _unused_frame, binding) -> None:
        LOGGER.info(f"Queue {self.queue_name} bound with {binding}")

    @no_type_check
    def on_scada_bindok(self, _unused_frame, binding) -> None:
        LOGGER.info(f"Queue {self.queue_name} bound with {binding}")

    def time(self) -> float:
        if self.universe_type == UniverseType.Dev:
            return self._time
        else:
            return time.time()

    def get_initial_time_s(self) -> float:
        if self.universe_type == UniverseType.Dev:
            return self.settings.initial_time_unix_s
        else:
            return time.time()

    def prepare_for_death(self) -> None:
        self.actor_main_stopped = True

    ########################
    ## Receives
    ########################

    def route_scada_message(self, from_alias: str, message: ScadaMessage) -> None:
        """Routes messages from the SCADA to methods that should be overwritten
        in derived class"""

        # if message.Header.Src != self.scada_alias:
        #     LOGGER.info(
        #         f"Ignoring scada message from {message.Header.Src}. My scada is {self.scada_alias}"
        #     )
        #     LOGGER.info(f"{message}")
        #     return
        if message.Header.AckRequired == True:
            payload = Ack(AckMessageID=message.Header.MessageId)
            self.send_scada_message(payload)

        path_dbg = 0
        match message.Payload:
            case GridworksPing():
                self._process_gridworks_ping_from_scada(
                    cast(GridworksPing, message.Payload)
                )
            case GtShStatusEvent():
                self._process_gt_sh_status_event_from_scada(
                    cast(GtShStatusEvent, message.Payload)
                )
            case PeerActiveEvent():
                self._process_peer_active_event_from_scada(
                    cast(PeerActiveEvent, message.Payload)
                )
            case SnapshotSpaceheatEvent():
                self._process_snapshot_spaceheat_event_from_scada(
                    cast(SnapshotSpaceheatEvent, message.Payload)
                )
            case PowerWatts():
                self._process_power_watts_from_scada(cast(PowerWatts, message.Payload))

            case SnapshotSpaceheat():
                self._process_snapshot_spaceheat_from_scada(
                    cast(SnapshotSpaceheat, message.Payload)
                )

    @abstractmethod
    def _process_gridworks_ping_from_scada(self, payload: GridworksPing) -> None:
        """Atn has received gridworks.ping message from its SCADA"""
        raise NotImplementedError

    @abstractmethod
    def _process_peer_active_event_from_scada(self, payload: PeerActiveEvent) -> None:
        """Atn has received gridworks.event.comm.peer.active message from its SCADA"""
        raise NotImplementedError

    def _process_gt_sh_status_event_from_scada(self, payload: GtShStatusEvent) -> None:
        """Atn has received gridworks.event.gt.sh.status message from its SCADA"""
        gt_sh_status = payload.status
        self._process_gt_sh_status_from_scada(payload=gt_sh_status)

    def _process_snapshot_spaceheat_event_from_scada(
        self, payload: SnapshotSpaceheatEvent
    ) -> None:
        """Atn has received  gridworks.event.snapshot.spaceheat message from its SCADA"""
        snapshot_spaceheat = payload.snap
        self._process_snapshot_spaceheat_from_scada(payload=snapshot_spaceheat)

    @abstractmethod
    def _process_gt_sh_status_from_scada(self, payload: GtShStatus) -> None:
        """Atn has received gt.sh.status message from its SCADA"""
        raise NotImplementedError

    @abstractmethod
    def _process_power_watts_from_scada(self, payload: PowerWatts) -> None:
        """Atn has received power.watts message from its SCADA"""
        raise NotImplementedError

    @abstractmethod
    def _process_snapshot_spaceheat_from_scada(self, payload: SnapshotSpaceheat):
        """Atn has received a snapshot.sspaceheat message from the SCADA"""
        raise NotImplementedError

    def route_message(
        self, from_alias: str, from_role: GNodeRole, payload: HeartbeatA
    ) -> None:
        self.payload = payload
        if payload.TypeName == HeartbeatA_Maker.type_name:
            if from_role != GNodeRole.Supervisor:
                LOGGER.info(
                    f"Ignoring HeartbeatA from GNode with role {from_role}; expects Supervisor"
                )
            try:
                self.heartbeat_from_super(from_alias, payload)
            except:
                LOGGER.exception("Error in heartbeat_received")
        elif payload.TypeName == HeartbeatB_Maker.type_name:
            if from_role != GNodeRole.Scada:
                LOGGER.info(
                    f"Ignoring HeartbeatB from GNode with role {from_role}; expects Scada"
                )
            try:
                self.heartbeat_from_scada(payload)
            except:
                LOGGER.exception("Error in heartbeat_from_partner")
        elif payload.TypeName == JoinDispatchContract_Maker.type_name:
            if from_role != GNodeRole.Scada:
                LOGGER.info(
                    f"Ignoring JoinDispatchContract from GNode with role {from_role}; expects Scada"
                )
            try:
                self.join_dispatch_contract_from_scada(payload)
            except:
                LOGGER.exception("join_dispatch_contract_from_scada")
        elif payload.TypeName == LatestPrice_Maker.type_name:
            if from_role == GNodeRole.MarketMaker:
                try:
                    self.latest_price_from_market_maker(payload)
                except:
                    LOGGER.exception("Error in latest_price_from_market_maker")
        elif payload.TypeName == SimTimestep_Maker.type_name:
            try:
                self.timestep_from_timecoordinator(payload)
            except:
                LOGGER.exception("Error in timestep_from_timecoordinator")

    def heartbeat_from_super(self, from_alias: str, ping: HeartbeatA) -> None:
        pong = HeartbeatA_Maker(
            my_hex=str(random.choice("0123456789abcdef")), your_last_hex=ping.MyHex
        ).tuple

        self.send_message(
            payload=pong,
            to_role=GNodeRole.Supervisor,
            to_g_node_alias=self.settings.my_super_alias,
        )

        LOGGER.debug(
            f"[{self.alias}] Sent HB: SuHex {pong.YourLastHex}, AtnHex {pong.MyHex}"
        )

    def heartbeat_from_scada(self, ping: HeartbeatB) -> None:
        """
        This is the Atn's half of the DispatchContract Heartbeat pattern.
        It:
          - Checks that it has opted into a DispatchContract
          - Checks the  FromGNodeInstanceId to validate Scada credentials
          - Checks that the scada correctly repeated last sent hex
          - Updates the last hex received (for use at the top of the next minute) along w time received
        [more info](https://gridworks.readthedocs.io/en/latest/dispatch-contract.html)

        Args:
            payload (HeartbeatB): The latest heartbeat received from its
            SCADA partner

        """
        if not self.in_dispatch_contract():
            LOGGER.info(f"Not in Dispatch Contract. Ignoring")
        if ping.FromGNodeInstanceId != self.scada_gni_id:
            raise Exception("In dispatch contract but mismatched Scada Gni Id!")
        if ping.YourLastHex != self.hb_status.AtnLastHex:
            LOGGER.info(f"Received incorrect pong. Ignoring")
            return
        self.hb_status.LastHeartbeatReceivedMs = int(time.time() * 1000)
        self.hb_status.ScadaLastHex = ping.MyHex
        self.hb_status.AtnLastHex = str(random.choice("0123456789abcdef"))
        LOGGER.info(f"Got {ping.MyHex}")
        # Does not send back. Atn waits for the DispatchContract's expected
        # one minute before sending.
        # print(f"Got heartbeat from scada: {ping}")

    def hb_to_scada(self):
        """Checks that Atn is in Dispatch Contract, sends a HeartbeatB to Scada,
        and then reports to DispatchContract"""
        if not self.in_dispatch_contract():
            LOGGER.info("Not sending hb to Scada - not in DispatchContract yet")
        ping = HeartbeatB_Maker(
            from_g_node_alias=self.alias,
            from_g_node_instance_id=self.g_node_instance_id,
            my_hex=self.hb_status.AtnLastHex,
            your_last_hex=self.hb_status.ScadaLastHex,
            last_received_time_unix_ms=self.hb_status.LastHeartbeatReceivedMs,
            send_time_unix_ms=int(1000 * time.time()),
        ).tuple
        self.send_message(
            payload=ping,
            to_role=GNodeRole.Scada,
            to_g_node_alias=self.scada_alias,
        )
        LOGGER.info(f"Sent  {ping.MyHex}")
        # report to DispatchContract
        ptxn = PaymentTxn(self.acct.addr, self.sp, self.dc_client.app_addr, 1000)
        self.dc_client.call(
            DispatchContract.heartbeat_algo_audit,
            signed_proof=TransactionWithSigner(ptxn, self.acct.as_signer()),
            heartbeat=ping.as_dict(),
        )

    def check_for_dispatch_contract(self):
        """Upon startup, see if already party of a dispatch contract,
        and if so start up the dc_client and set the dc_app_id"""
        apps = self.client.account_info(self.acct.addr)["apps-local-state"]
        if len(apps) > 1:
            raise Exception("Should only be part of one app")
        if len(apps) == 0:
            return
        self.dc_app_id = apps[0]["id"]
        self.dc_client = ApplicationClient(
            client=self.client,
            app=DispatchContract(),
            signer=self.acct.as_signer(),
            app_id=self.dc_app_id,
        )

    def update_trading_rights(self) -> None:
        """Look at address to find our trading rights"""
        balances = algo_utils.get_balances(self.client, self.acct.addr)
        non_algo_asas = list(set(balances.keys()) - {0})
        ta_trading_rights = list(
            filter(
                lambda x: self.client.asset_info(x)["params"]["unit-name"] == "TATRADE",
                non_algo_asas,
            )
        )
        if len(ta_trading_rights) != 1:
            return
        x = ta_trading_rights[0]
        if self.client.asset_info(x)["params"]["name"] != self.ta_alias:
            raise Exception(
                f"Mismatch in trading rights and Alias. {self.alias} and {x}"
            )
        self.trading_rights_id = GwCertId_Maker(
            type=AlgoCertType.ASA, idx=ta_trading_rights[0], addr=None
        ).tuple

    def join_dispatch_contract_from_scada(self, payload: JoinDispatchContract) -> None:
        """Bootstraps the DispatchContract, opts in, and sends back DispatchContractConfirmed

        - ignores if already opted into a DispatchContract
        - Until World registry is in place, update g node instance id and write to .env
        - sets up ApplicationClient using the app_id sent by the scada
        - Checks that scada bootstrapping is done (contract has ta_alias and scada_cert_idx)
        - Check that our Atn acct owns the TaTradingRights for this TaAlias

        """
        if self.in_dispatch_contract():
            LOGGER.warning(
                f"Ignoring JoinDispatchContract - already in dispatch contract {self.dc_app_id}"
            )
            return
        self.scada_gni_id = payload.FromGNodeInstanceId
        with open(".env", "a") as file:
            file.write(f'ATN_SCADA_GNI_ID="{payload.FromGNodeInstanceId}"\n')
        self.dc_client = ApplicationClient(
            client=self.client,
            app=DispatchContract(),
            signer=self.acct.as_signer(),
            app_id=payload.DispatchContractAppId,
        )
        self.dc_app_id = payload.DispatchContractAppId
        app_state = self.dc_client.get_application_state()
        if not {"ta_alias", "scada_cert_idx"}.issubset(set(app_state.keys())):
            LOGGER.warning(
                f"AppId {payload.DispatchContractAppId} not done with scada bootstrap!"
            )
            return
        if not self.ta_alias == app_state["ta_alias"]:
            LOGGER.warning(
                f"Wrong TaAlias. Mine is {self.ta_alias}, DispatchContract has {app_state['ta_alias']}"
            )

        if self.trading_rights_id is None:
            self.update_trading_rights()
        if self.trading_rights_id is None:
            LOGGER.warning(f"Do not have trading rights! Cannot join dispatch contract")
            return
        ptxn = PaymentTxn(self.acct.addr, self.sp, self.dc_client.app_addr, 100_000)

        try:
            result = self.dc_client.call(
                DispatchContract.bootstrap2,
                atn_seed=TransactionWithSigner(ptxn, self.acct.as_signer()),
                TaTradingRights=self.trading_rights_id.Idx,
            )
        except Exception as e:
            LOGGER.warning(f"Failed to bootstrap DispatchContract: {e}")
            return

        # opts in
        self.dc_client.opt_in()
        LOGGER.info(f"Dispatch Contract {self.dc_app_id} is live")

        # sends back DispatchContractConfirmed

        txn = PaymentTxn(
            sender=self.acct.addr,
            receiver=self.dc_client.app_addr,
            sp=self.sp,
            amt=1000,
        )
        signed_txn = txn.sign(self.acct.sk)
        # don't need to actually send transaction for sig
        payload = DispatchContractConfirmed_Maker(
            from_g_node_alias=self.alias,
            from_g_node_instance_id=self.g_node_instance_id,
            signed_proof=encoding.msgpack_encode(signed_txn),
            atn_params=self.atn_params,
        ).tuple
        self.send_message(
            payload=payload, to_role=GNodeRole.Scada, to_g_node_alias=self.scada_alias
        )

    @abstractmethod
    def latest_price_from_market_maker(self, payload: LatestPrice) -> None:
        raise NotImplementedError

    def timestep_from_timecoordinator(self, payload: SimTimestep):
        if self._time == 0:
            self._time = payload.TimeUnixS
            self.new_timestep(payload)
            LOGGER.info(f"TIME STARTED: {self.time_str()}")
        elif self._time < payload.TimeUnixS:
            self._time = payload.TimeUnixS
            self.new_timestep(payload)
            LOGGER.debug(f"Time is now {self.time_str()}")
        elif self._time == payload.TimeUnixS:
            self.repeat_timestep(payload)

    @abstractmethod
    def new_timestep(self, payload: SimTimestep) -> None:
        # LOGGER.info("New timestep in atn_actor_base")
        raise NotImplementedError

    @abstractmethod
    def repeat_timestep(self, payload: SimTimestep) -> None:
        # LOGGER.info("Timestep received again in atn_actor_base")
        raise NotImplementedError

    def time_str(self) -> str:
        return pendulum.from_timestamp(self.time()).strftime("%m/%d/%Y, %H:%M")

    @property
    def ta_alias(self):
        """Add `ta` to the and of the Atn's GNodeAlias"""
        return self.alias + ".ta"

    @property
    def scada_alias(self):
        """Add `scada` from the end of the Atn's's GNodeAlias"""
        return self.alias + ".scada"

    def in_dispatch_contract(self) -> bool:
        """Checks that bootstrap 2 was completed w addition of ta_trading_rights_idx,
        and also that Scada is opted in"""
        if self.dc_client is None:
            return False
        app_state = self.dc_client.get_application_state()
        if "ta_trading_rights_idx" not in app_state.keys():
            return False
        # Todo: also check that atn is opted in
        apps = self.client.account_info(self.acct.addr)["apps-local-state"]
        app_ids = list(map(lambda x: x["id"], apps))
        if self.dc_client.app_id in app_ids:
            return True
        return False
