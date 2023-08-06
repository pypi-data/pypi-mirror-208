import logging
import time

import dotenv
import rich
from gwproto.messages import PeerActiveEvent
from gwproto.messages import Ping as GridworksPing

import gwatn.config as config
from gwatn.atn_actor_base import AtnActorBase
from gwatn.enums import TelemetryName
from gwatn.types import GtDispatchBoolean_Maker
from gwatn.types import GtShCliAtnCmd_Maker
from gwatn.types import GtShStatus
from gwatn.types import LatestPrice
from gwatn.types import PowerWatts
from gwatn.types import SimTimestep
from gwatn.types import SnapshotSpaceheat


LOG_FORMAT = (
    "%(levelname) -10s %(sasctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)


class SimpleAtnActor(AtnActorBase):
    """Simple implementation of an AtnActor, for testing purposes"""

    def __init__(
        self,
        settings: config.AtnSettings = config.AtnSettings(
            _env_file=dotenv.find_dotenv()
        ),
    ):
        super().__init__(settings=settings)
        self._power_watts: int = 0
        LOGGER.info("Simple Atn Initialized")

    def latest_price_from_market_maker(self, payload: LatestPrice) -> None:
        pass

    def new_timestep(self, payload: SimTimestep) -> None:
        """Set to work with a timestep per minute"""

        # sends a hb to Scada every minute for DispatchContract
        if self.in_dispatch_contract():
            self.hb_to_scada()

    def repeat_timestep(self, payload: SimTimestep) -> None:
        pass

    ##################
    # Sent to SCADA
    ##################

    def snap(self):
        self.send_scada_message(
            payload=GtShCliAtnCmd_Maker(
                from_g_node_alias=self.alias,
                from_g_node_id=self.g_node_instance_id,
                send_snapshot=True,
            ).tuple
        )

    def turn_on(self, relay_node_name: str) -> None:
        self.send_scada_message(
            payload=GtDispatchBoolean_Maker(
                about_node_name=relay_node_name,
                to_g_node_alias=self.scada_alias,
                from_g_node_alias=self.alias,
                from_g_node_instance_id=self.g_node_instance_id,
                relay_state=1,
                send_time_unix_ms=int(time.time() * 1000),
            ).tuple
        )

    def turn_off(self, relay_node_name: str) -> None:
        self.send_scada_message(
            payload=GtDispatchBoolean_Maker(
                about_node_name=relay_node_name,
                to_g_node_alias=self.scada_alias,
                from_g_node_alias=self.alias,
                from_g_node_instance_id=self.g_node_instance_id,
                relay_state=0,
                send_time_unix_ms=int(time.time() * 1000),
            ).tuple
        )

    ######################
    # Received from SCADA
    #####################
    def _process_gridworks_ping_from_scada(self, payload: GridworksPing) -> None:
        """Atn has received gridworks.ping message from its SCADA"""
        ...
        LOGGER.debug(f"_process_gridworks_ping_from_scada: {payload}")

    def _process_peer_active_event_from_scada(self, payload: PeerActiveEvent) -> None:
        """Atn has received gridworks.event.comm.peer.active message from its SCADA"""
        LOGGER.debug(f"_process_peer_active_event_from_scada: {payload}")

    def _process_gt_sh_status_from_scada(self, payload: GtShStatus) -> None:
        """Atn has received gt.sh.status message from its SCADA"""
        self.latest_status = payload
        LOGGER.debug(f"_process_gt_sh_status_from_scada: {payload}")

    def _process_power_watts_from_scada(self, payload: PowerWatts) -> None:
        """Atn has received power.watts message from its SCADA"""
        rich.print(f"Agg Power {payload.Watts} W")
        self._power_watts = payload.Watts

    def _process_snapshot_spaceheat_from_scada(
        self, payload: SnapshotSpaceheat
    ) -> None:
        """Atn has received gridworks.event.snapshot.spaceheat message from its SCADA"""
        s = "\n\nSnapshot received:\n"
        for i in range(len(payload.Snapshot.AboutNodeAliasList)):
            telemetry_name = payload.Snapshot.TelemetryNameList[i]
            if telemetry_name == TelemetryName.WaterTempCTimes1000:
                centigrade = payload.Snapshot.ValueList[i] / 1000
                fahrenheit = (centigrade * 9 / 5) + 32
                extra = f"{fahrenheit:5.2f} F"
            elif telemetry_name == TelemetryName.WaterTempFTimes1000:
                fahrenheit = payload.Snapshot.ValueList[i] / 1000
                extra = f"{fahrenheit:5.2f} F"
            else:
                extra = (
                    f"{payload.Snapshot.ValueList[i]} "
                    f"{payload.Snapshot.TelemetryNameList[i].value}"
                )
            s += f"  {payload.Snapshot.AboutNodeAliasList[i]}: {extra}\n"
        LOGGER.info(s)
