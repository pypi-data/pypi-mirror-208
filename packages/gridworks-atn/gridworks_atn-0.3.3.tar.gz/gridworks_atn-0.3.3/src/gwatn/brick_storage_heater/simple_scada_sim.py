""" SCADA Actor """
import functools
import logging
import time
from typing import Optional
from typing import cast

import dotenv
import pendulum
from gridworks.enums import GNodeRole
from pydantic import BaseModel

import gwatn.api_types as api_types
import gwatn.config as config
from gwatn.simple_scada_sim_actor_base import SimpleScadaSimActorBase
from gwatn.types import AtnParamsBrickstorageheater as AtnParams
from gwatn.types import AtnParamsBrickstorageheater_Maker
from gwatn.types import GtDispatchBoolean
from gwatn.types import SimplesimDriverDataBsh
from gwatn.types import SimplesimDriverDataBsh_Maker
from gwatn.types import SimplesimDriverReport
from gwatn.types import SimplesimSnapshotBrickstorageheater as Snapshot
from gwatn.types import SimTimestep


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


class SimpleScadaSim__BrickStorageHeater(SimpleScadaSimActorBase):
    def __init__(
        self,
        settings: config.ScadaSettings = config.ScadaSettings(
            _env_file=dotenv.find_dotenv()
        ),
    ):
        super().__init__(settings=settings)
        self.api_type_maker_by_name = api_types.TypeMakerByName
        self.atn_params_type_name = AtnParamsBrickstorageheater_Maker.type_name
        self.power_watts: float = 0
        self.store_kwh: int = 0
        self.max_store_kwh: int = 0
        self.atn_params: Optional[AtnParams] = None

    ########################
    ## Receives
    ########################

    #########################################################
    # Make the below into abstractmethods if pulling out base class
    #########################################################

    def simplesim_driver_report_received(self, payload: SimplesimDriverReport) -> None:
        """This gets received right before the top of the hour, from our
        best simulation of the TerminalAsset (which is happening in the
        AtomicTNode)."""
        if payload.FromGNodeInstanecId != self.atn_gni_id:
            LOGGER.info(f"Igoring {payload} - incorrect GNodeInstanceId")

        if payload.DriverDataTypeName != SimplesimDriverDataBsh_Maker.type_name:
            LOGGER.info(
                f"Igoring {payload} - incorrect DriverDataTypeName. "
                f"Expected {SimplesimDriverDataBsh_Maker.type_name} but got {payload.DriverDataTypeName}"
            )
        data = cast(SimplesimDriverDataBsh, payload.DriverData)
        self.power_watts = data.PowerWatts
        self.store_kwh = data.StoreKwh
        self.max_store_kwh = data.MaxStoreKwh
        self.send_snapshot()

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
