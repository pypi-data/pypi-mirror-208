""" SCADA Actor """
import functools
import logging
import random
import time
from typing import Optional
from typing import no_type_check

import dotenv
import gridworks.algo_utils as algo_utils
import pendulum
import requests
from algosdk.atomic_transaction_composer import TransactionWithSigner
from algosdk.future.transaction import *
from algosdk.v2client.algod import AlgodClient
from beaker.client import ApplicationClient
from gridworks.actor_base import ActorBase
from gridworks.algo_utils import BasicAccount
from gridworks.enums import GNodeRole
from gridworks.message import as_enum
from pydantic import BaseModel

import gwatn.api_types as api_types
import gwatn.config as config
from gwatn import DispatchContract
from gwatn.enums import AlgoCertType
from gwatn.enums import MessageCategorySymbol
from gwatn.enums import UniverseType
from gwatn.types import AtnParamsBrickstorageheater as AtnParams
from gwatn.types import DispatchContractConfirmed
from gwatn.types import DispatchContractConfirmed_Maker
from gwatn.types import GtDispatchBoolean
from gwatn.types import GtDispatchBoolean_Maker
from gwatn.types import GwCertId
from gwatn.types import GwCertId_Maker
from gwatn.types import HeartbeatA
from gwatn.types import HeartbeatA_Maker
from gwatn.types import HeartbeatB
from gwatn.types import HeartbeatB_Maker
from gwatn.types import JoinDispatchContract_Maker
from gwatn.types import ScadaCertTransfer_Maker
from gwatn.types import SimplesimDriverReport
from gwatn.types import SimplesimDriverReport_Maker
from gwatn.types import SimTimestep
from gwatn.types import SimTimestep_Maker
from gwatn.types import SnapshotBrickstorageheater as Snapshot


DISPATCH_CONTRACT_REPORTING_ALGOS = 5

LOG_FORMAT = (
    "%(levelname) -10s %(sasctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)

LOGGER.setLevel(logging.INFO)


def get_max_store_kwh_th(params: AtnParams) -> float:
    room_temp_c = (params.RoomTempF - 32) * 5 / 9
    return params.C * (params.MaxBrickTempC - room_temp_c)


class AtnHbStatus(BaseModel):
    LastHeartbeatReceivedMs: int
    AtnLastHex: Optional[str] = None
    ScadaLastHex: str = "0"


class SimpleScadaSimActorBase(ActorBase):
    def __init__(
        self,
        settings: config.ScadaSettings = config.ScadaSettings(
            _env_file=dotenv.find_dotenv()
        ),
    ):
        super().__init__(settings=settings)

        self.settings = settings
        self.atn_gni_id = settings.atn_gni_id
        self.acct: BasicAccount = BasicAccount(settings.sk.get_secret_value())
        self.client: AlgodClient = AlgodClient(
            settings.algo_api_secrets.algod_token.get_secret_value(),
            settings.public.algod_address,
        )
        self.atn_params_type_name: str = "atn.params.brickstorageheater"
        self.sp = self.client.suggested_params()
        self.cert_id: Optional[GwCertId] = None
        self.talking_with: bool = False
        self.atn_hb_status = AtnHbStatus(
            LastHeartbeatReceivedMs=int(1000 * time.time())
        )
        # The dc_client (DispatchContract client) builds on top of the Algorand beaker ApplicationClient
        self.dc_client: Optional[ApplicationClient] = None
        self.dc_app_id: Optional[int] = None
        self.algo_init_check()
        self.universe_type = as_enum(
            self.settings.universe_type_value, UniverseType, UniverseType.default()
        )
        self._time: float = self.get_initial_time_s()
        self.api_type_maker_by_name = (
            api_types.TypeMakerByName
        )  # overwrites base class to include types used in this repo
        self.atn_params_type_name: str = "atn.params"  # overwrite in the subclass

    @property
    def atn_alias(self):
        """Removes `scada` from the end of the SCADA's GNodeAlias"""
        return self.alias[:-6]

    @property
    def ta_alias(self):
        """Removes `scada` from the end of the SCADA's GNodeAlias"""
        return self.atn_alias + ".ta"

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

    @no_type_check
    def on_timecoordinator_bindok(self, _unused_frame, binding) -> None:
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

    def route_message(
        self, from_alias: str, from_role: GNodeRole, payload: HeartbeatB
    ) -> None:
        if payload.TypeName == DispatchContractConfirmed_Maker.type_name:
            if from_role != GNodeRole.AtomicTNode:
                LOGGER.info(
                    f"Ignoring DispatchContractConfrimed from GNode with role {from_role}; expects AtomicTNode"
                )
            try:
                self.dispatch_contract_confirmed_received(payload)
            except:
                LOGGER.exception("Error in dispatch_contract_confirmed_received")
        elif payload.TypeName == GtDispatchBoolean_Maker.type_name:
            if from_role != GNodeRole.AtomicTNode:
                LOGGER.info(
                    f"Ignoring GtDispatchBooleanfrom GNode with role {from_role}; expects AtomicTNode"
                )
            try:
                self.dispatch_received(payload)
            except:
                LOGGER.exception("Error in dispatch_received")

        elif payload.TypeName == HeartbeatA_Maker.type_name:
            if from_role != GNodeRole.Supervisor:
                LOGGER.info(
                    f"Ignoring HeartbeatA from GNode with role {from_role}; expects Supervisor"
                )
            try:
                self.heartbeat_from_super(from_alias=from_alias, ping=payload)
            except:
                LOGGER.exception("Error in heartbeat_from_super")
        elif payload.TypeName == HeartbeatB_Maker.type_name:
            if from_role != GNodeRole.AtomicTNode:
                LOGGER.info(
                    f"Ignoring HeartbeatB from GNode with role {from_role}; expects AtomicTNode"
                )
            try:
                self.heartbeat_from_atn(ping=payload)
            except:
                LOGGER.exception("Error in heartbeat_from_atn")
        elif payload.TypeName == SimplesimDriverReport_Maker.type_name:
            try:
                self.simplesim_driver_report_received(payload)
            except:
                LOGGER.exception("Error in simplesim_driver_report_received")
        elif payload.TypeName == SimTimestep_Maker.type_name:
            if from_role != GNodeRole.TimeCoordinator:
                LOGGER.info(
                    f"Ignoring SimTimestep from GNode with role {from_role}; expects TimeCoordinator"
                )
            try:
                self.timestep_from_timecoordinator(payload)
            except:
                LOGGER.exception("Error in timestep_from_timecoordinator")

    def heartbeat_from_atn(self, ping: HeartbeatB) -> None:
        """
        This is the Scada's half of the DispatchContract Heartbeat pattern.
        It:
          - Checks that it has a DispatchContract (owns that SmartContract)
          - Checks the GNodeAlias and GNodeInstanceId to validate partner
          - Sends a reply HeartbeatB immediately back using a RabbitJsonDirect message
          - Sends an audit report of its action to the DispatchContract
            # TODO: save audit report for sending in a batch if SmartContract
            # exists but is not reachable (i.e. blockchain down)
        [more info](https://gridworks.readthedocs.io/en/latest/dispatch-contract.html)

        Args:
            payload (HeartbeatB): The latest heartbeat received from its
            AtomicTNode partner

        """
        self.ping = ping

        received_ms = int(time.time() * 1000)
        if not self.in_dispatch_contract():
            LOGGER.info(f"Not in Dispatch Contract. Ignoring")
        if ping.FromGNodeInstanceId != self.atn_gni_id:
            raise Exception("In dispatch contract but mismatched Atn Gni Id!")
        if self.atn_hb_status.AtnLastHex is not None:
            if ping.YourLastHex != self.atn_hb_status.ScadaLastHex:
                LOGGER.info("Received incorrect ping. Ignoring")
                return
        self.talking_with = True
        self.atn_hb_status.LastHeartbeatReceivedMs = int(time.time() * 1000)
        self.atn_hb_status.AtnLastHex = ping.MyHex
        self.atn_hb_status.ScadaLastHex = str(random.choice("0123456789abcdef"))
        LOGGER.info(f"Got {ping.MyHex}. Sending {self.atn_hb_status.ScadaLastHex}")
        pong = HeartbeatB_Maker(
            from_g_node_alias=self.alias,
            from_g_node_instance_id=self.g_node_instance_id,
            my_hex=self.atn_hb_status.ScadaLastHex,
            your_last_hex=self.atn_hb_status.AtnLastHex,
            last_received_time_unix_ms=self.atn_hb_status.LastHeartbeatReceivedMs,
            send_time_unix_ms=int(1000 * time.time()),
        ).tuple
        self.send_message(
            payload=pong, to_role=GNodeRole.AtomicTNode, to_g_node_alias=self.atn_alias
        )
        # Report to DispatchContract with heartbeat.algo.audit
        ptxn = PaymentTxn(self.acct.addr, self.sp, self.dc_client.app_addr, 1000)
        self.dc_client.call(
            DispatchContract.heartbeat_algo_audit,
            signed_proof=TransactionWithSigner(ptxn, self.acct.as_signer()),
            heartbeat=pong.as_dict(),
        )

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

    ########################################################
    #  Related to Dispatch Contract and Scada Cert
    ########################################################

    def algo_init_check(self):
        """Upon startup, see if the dispatch contract has already been created
        and also make sure Scada is appropriately funded"""

        # First, request cert transfer. This is idempotent - if scada
        # addr already owns the ScadaCertificate it does nothing

        self.request_cert_transfer()
        apps = self.client.account_info(self.acct.addr)["created-apps"]
        balances = algo_utils.get_balances(self.client, self.acct.addr)
        micro_algos = balances[0]
        if micro_algos < 100_000:
            raise Exception(f"Insufficient funds to even opt into SCADA cert!")
        if len(apps) > 1:
            raise Exception("Should only be part of one app")
        if not self.dispatch_contract_created():
            # Create, fund and do bootstrap1 of the Dispatch contract
            dc_algos = DISPATCH_CONTRACT_REPORTING_ALGOS + (
                DispatchContract.min_balance / 1_000_000
            )
            if micro_algos < (dc_algos + 2) * 1_000_000:
                raise Exception(f"Insufficient funding! Need at least {dc_algos + 2}")
            self.dc_client = ApplicationClient(
                self.client, DispatchContract(), signer=self.acct.as_signer()
            )
            app_id, app_address, transaction_id = self.dc_client.create()
            self.dc_app_id = app_id
            LOGGER.info(f"Created Dispatch Contract, app id {self.dc_app_id}")
            sp = self.dc_client.get_suggested_params()
            sp.flat_fee = True
            sp.fee = 2000
            ptxn = PaymentTxn(
                self.acct.addr,
                sp,
                self.dc_client.app_addr,
                DispatchContract.min_balance,
            )

            # Now do the first half of bootstrapping the contract by providing it
            # with enough money to fund about 32kB in boxes, along with
            # our ScadaCertId (which can be shown to match our address in the sig)

            result = self.dc_client.call(
                DispatchContract.bootstrap1,
                scada_seed=TransactionWithSigner(ptxn, self.acct.as_signer()),
                ScadaCert=self.cert_id.Idx,
            )
            LOGGER.info("Called bootstrap1 method of DispatchContract")
            LOGGER.info(
                f"Providing the scada certificate, and funding with {dc_algos} Algos"
            )
            if result.return_value != self.ta_alias:
                raise Exception(
                    f"Expected {self.ta_alias} back from bootstrapping app {self.dc_app_id}, but"
                    f" got {result.return_value}"
                )
        else:
            created_apps = self.client.account_info(self.acct.addr)["created-apps"]
            self.dc_app_id = created_apps[0]["id"]
            self.dc_client = ApplicationClient(
                client=self.client,
                app=DispatchContract(),
                signer=self.acct.as_signer(),
                app_id=self.dc_app_id,
            )
            LOGGER.info(f"Dispatch contract already exists, app id {self.dc_app_id}")
        self.in_dispatch_contract()

    def request_cert_transfer(self) -> None:
        """
        Opts into certificate and then request transfer of the ScadaCert from the GNodeFactory

        Raises:
            Exception if the scada certificate does not exist, or transfer is not successful
        """
        cert_type = AlgoCertType(self.settings.cert_type_value)
        if cert_type == AlgoCertType.SmartSig:
            raise NotImplementedError("Not prepared for SmartSig Certificates yet")

        # Look for cert id
        gnf = self.settings.public.gnf_admin_addr
        a = self.client.account_info(gnf)["created-assets"]
        scada_nft_ids = list(
            filter(
                lambda x: x["params"]["unit-name"] == "SCADA"
                and x["params"]["name"] == self.ta_alias,
                a,
            )
        )
        if len(scada_nft_ids) == 0:
            raise Exception("Scada certificate does not exist")

        self.cert_id = GwCertId_Maker(
            type=AlgoCertType.ASA, idx=scada_nft_ids[0]["index"], addr=None
        ).tuple

        balances = algo_utils.get_balances(self.client, self.acct.addr)

        # First, opt into sig
        txn = AssetOptInTxn(self.acct.addr, self.sp, self.cert_id.Idx)

        signed_txn = txn.sign(self.acct.sk)
        if self.cert_id.Idx not in balances.keys():
            try:
                self.client.send_transaction(signed_txn)
            except:
                raise Exception(
                    "Failure sending transaction on Algo blockchain. Check sandbox and funding"
                )
            algo_utils.wait_for_transaction(self.client, signed_txn.get_txid())

        balances = algo_utils.get_balances(self.client, self.acct.addr)

        if balances[self.cert_id.Idx] == 1:
            # already own the cert
            return
        payload = ScadaCertTransfer_Maker(
            ta_alias="d1.isone.ver.keene.holly.ta",  # REPLACE WITH api_util.get_alias_from_scada_cert
            signed_proof=encoding.msgpack_encode(signed_txn),
        ).tuple

        api_endpoint = f"{self.settings.public.gnf_api_root}/scada-cert-transfer/"
        try:
            r = requests.post(url=api_endpoint, json=payload.as_dict())
        except:
            raise Exception(f"Post to {api_endpoint} failed")
        if r.status_code > 200:
            if r.status_code == 422:
                note = f"Error entering SLA: " + r.json()["detail"]
            else:
                note = r.reason
            raise Exception(f"Post to {api_endpoint} failed: {note} ")

        # check that scada now owns cert
        balances = algo_utils.get_balances(self.client, self.acct.addr)
        if balances[self.cert_id.Idx] != 1:
            raise Exception(f"Gnf claimed successful transfer but I do not own cert")

        LOGGER.info(f"Successfully received Scada Cert ASA {self.cert_id.Idx}")

    def initialize_dispatch_contract(self):
        """Starts up Dispatch contract to be used with AtomicTNode.


        Raises exception if Scada Addr
            - scada cert from settings matches what is in my acct
            - already has created an app
            - does not already have a unique Scada Cert ASA
        """

        if self.in_dispatch_contract():
            LOGGER.warning(
                f"Already in dispatch contract. Ignoring initialize_dispatch_contract!"
            )
            return

        balances = algo_utils.get_balances(self.client, self.acct.addr)
        non_algo_asas = list(set(balances.keys()) - {0})
        scada_certs = list(
            filter(
                lambda x: self.client.asset_info(x)["params"]["unit-name"] == "SCADA",
                non_algo_asas,
            )
        )

        if len(scada_certs) > 1:
            raise Exception(
                f"Scada {self.alias} has 2 scada certs. This should not happen!"
            )
        if len(scada_certs) == 0:
            raise Exception(
                "Scada acct needs to be created and funded by TaOwner, and Scada GNode "
                "needs to be authorized (with GNodeFactory sending Scada cert) "
                f"before starting up {self.alias}"
            )

        if self.cert_id.Idx != scada_certs[0]:
            raise Exception(
                f"Scada cert in settings {self.cert_id.Idx} does not match"
                f"scada cert in my acct {scada_certs[0]}"
            )

        txn = PaymentTxn(
            sender=self.acct.addr,
            receiver=self.dc_client.app_addr,
            sp=self.sp,
            amt=1000,
        )
        signed_txn = txn.sign(self.acct.sk)
        # Don't need to actually send it in order to establish signature
        payload = JoinDispatchContract_Maker(
            from_g_node_alias=self.alias,
            from_g_node_instance_id=self.g_node_instance_id,
            dispatch_contract_app_id=self.dc_app_id,
            signed_proof=encoding.msgpack_encode(signed_txn),
        ).tuple

        self.send_message(
            payload=payload,
            to_role=GNodeRole.AtomicTNode,
            to_g_node_alias=self.atn_alias,
        )
        LOGGER.info(f"Sent d = {payload.as_dict()}")

    def dispatch_contract_confirmed_received(self, payload: DispatchContractConfirmed):
        """Check the state of the app to confirm that the Atn has finished the bootstrap.
        Then
           - set the atn_gni_id to GNodeInstanceId from the payload (this is how the Scada
           will confirm identity of the AtomicTNode
           - set the atn_params to those shared by the AtomicTNode
           - opt into the Dispatch Contract (now the DispatchContract is live)"""
        if self.dc_app_id is None:
            raise Exception(
                "Thats odd ... dont have a Dispatch Contract App Id and I need to be"
                "the creator"
            )
        if self.in_dispatch_contract():
            LOGGER.warning(
                f"Ignoring DispatchContractConfirmed - already in dispatch contract {self.dc_app_id}"
            )
            return

        if payload.AtnParamsTypeName != self.atn_params_type_name:
            LOGGER.info(
                f"Unexpected AtnParamsTypeName {payload.AtnParamsTypeName}. Expects {self.atn_params_type_name}"
            )
            return
        self.atn_params = payload.Params
        app_state = self.dc_client.get_application_state()
        if "ta_trading_rights_idx" not in app_state.keys():
            LOGGER.warning(f"Atn bootstrap is not finished. Ignoring")
            return

        self.atn_gni_id = payload.FromGNodeInstanceId

        with open(".env", "a") as file:
            file.write(f'SCADA_ATN_GNI_ID="{payload.FromGNodeInstanceId}"\n')
        self.dc_client.opt_in()
        LOGGER.info(f"Dispatch Contract {self.dc_app_id} is live")

    #########################################################
    # Make the below into abstractmethods if pulling out base class
    #########################################################

    def simplesim_driver_report_received(self, payload: SimplesimDriverReport) -> None:
        """This gets received right before the top of the hour, from our
        best simulation of the TerminalAsset (which is happening in the
        AtomicTNode).

        Should be overwritten by the derived class, according to the
        DriverDataTypeName. Should then send snapshot."""
        if payload.FromGNodeInstanecId != self.atn_gni_id:
            LOGGER.info(f"Igoring {payload} - incorrect GNodeInstanceId")

    def send_snapshot(self):
        """Send a snapshot of current core sensed values to AtomicTNode.
        This is done every hour, and also on sensed power change."""
        if self.atn_params is None:
            return
        report_payload = Snapshot(
            FromGNodeAlias=self.alias,
            FromGNodeInstanceId=self.g_node_instance_id,
            PowerWatts=self.power_watts,
            StoreKwh=self.store_kwh,
            MaxStoreKwh=get_max_store_kwh_th(self.atn_params),
            AboutTerminalAssetAlias=self.ta_alias,
        )
        self.send_message(
            payload=report_payload,
            to_role=GNodeRole.AtomicTNode,
            to_g_node_alias=self.atn_alias,
        )

    def dispatch_received(self, payload: GtDispatchBoolean) -> None:
        """
        Dispatch received from AtomicTNode

          - Checks that the GNodeAlias and GNodeInstanceId belong to its
        AtomicTNode and that we have a dispatch contract
          - Sets talking_with to true
          - Follows instructions (turns on or turns off). Will turn on or
          off boost unless AboutNodeName is "a.element"

        For hourly sim:
          - Updatespower
          - Send status to AtomicTNode
        """
        if self.atn_params is None or self.in_dispatch_contract() is False:
            LOGGER.info("Igoring dispatch command, DispatchContract is not started")
        if payload.FromGNodeInstanceId != self.atn_gni_id:
            LOGGER.info(f"Igoring {payload}, not my Atn's GNodeInstanceId")
        self.talking_with = True
        if payload.AboutNodeName == "a.elements":
            # Making the grossly simplifying assumption that the heat pump turns on immediately
            if payload.RelayState == 1:
                new_power_watts = self.atn_params.RatedMaxPowerKw * 1000
            else:
                new_power_watts = 0
            if self.power_watts != new_power_watts:
                self.power_watts = new_power_watts
                self.send_snapshot()

    def new_timestep(self, payload: SimTimestep) -> None:
        # LOGGER.info("New timestep")
        if not self.in_dispatch_contract():
            self.initialize_dispatch_contract()

    def repeat_timestep(self, payload: SimTimestep) -> None:
        LOGGER.info("Timestep received again")

    def time_str(self) -> str:
        return pendulum.from_timestamp(self.time()).strftime("%m/%d/%Y, %H:%M")

    def dispatch_contract_created(self) -> bool:
        """The SCADA only creates one kind of smart contract, which is its dispatch contract.
        So this just checks for a created app
        """
        created_apps = self.client.account_info(self.acct.addr)["created-apps"]
        if len(created_apps) > 1:
            raise NotImplementedError(
                f"SCADA not designed yet to create multiple dispatch contracts"
            )
        if len(created_apps) > 0:
            return True
        return False

    def in_dispatch_contract(self) -> bool:
        """Checks that bootstrap 2 was completed w addition of ta_trading_rights_idx,
        and also that Scada is opted in"""
        app_state = self.dc_client.get_application_state()
        if "ta_trading_rights_idx" not in app_state.keys():
            LOGGER.info(
                "Not in Dispatch Contract because ta_trading_rights_idx isn't in app_state"
            )
            LOGGER.info(
                "AtomicTNode has not finished its part in bootstrapping the contract"
            )
            return False
        # Todo: also check that atn is opted in
        apps = self.client.account_info(self.acct.addr)["apps-local-state"]
        app_ids = list(map(lambda x: x["id"], apps))
        if self.dc_client.app_id in app_ids:
            return True
        LOGGER.info(
            "Not in Dispatch Contract because scada has not yet opted into contract"
        )
        return False
