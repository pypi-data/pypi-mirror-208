""" List of all the types used"""
from typing import Dict
from typing import List
from typing import no_type_check

from gwatn.types import AcceptedBid_Maker
from gwatn.types import AtnBid_Maker
from gwatn.types import AtnParams_Maker
from gwatn.types import AtnParamsBrickstorageheater_Maker
from gwatn.types import AtnParamsReport_Maker
from gwatn.types import BaseGNodeGt_Maker
from gwatn.types import BasegnodeScadaCreate_Maker
from gwatn.types import ComponentAttributeClassGt_Maker
from gwatn.types import ComponentGt_Maker
from gwatn.types import DataChannel_Maker
from gwatn.types import DiscoverycertAlgoCreate_Maker
from gwatn.types import DispatchContractConfirmed_Maker
from gwatn.types import EgaugeIo_Maker
from gwatn.types import EgaugeRegisterConfig_Maker
from gwatn.types import ElectricMeterCacGt_Maker
from gwatn.types import ElectricMeterComponentGt_Maker
from gwatn.types import FloParams_Maker
from gwatn.types import FloParamsBrickstorageheater_Maker
from gwatn.types import FloParamsReport_Maker
from gwatn.types import GNodeGt_Maker
from gwatn.types import GNodeInstanceGt_Maker
from gwatn.types import GtDispatchBoolean_Maker
from gwatn.types import GtDispatchBooleanLocal_Maker
from gwatn.types import GtDriverBooleanactuatorCmd_Maker
from gwatn.types import GtShBooleanactuatorCmdStatus_Maker
from gwatn.types import GtShCliAtnCmd_Maker
from gwatn.types import GtShMultipurposeTelemetryStatus_Maker
from gwatn.types import GtShSimpleTelemetryStatus_Maker
from gwatn.types import GtShStatus_Maker
from gwatn.types import GtShTelemetryFromMultipurposeSensor_Maker
from gwatn.types import GtTelemetry_Maker
from gwatn.types import GwCertId_Maker
from gwatn.types import HeartbeatA_Maker
from gwatn.types import HeartbeatB_Maker
from gwatn.types import InitialTadeedAlgoCreate_Maker
from gwatn.types import InitialTadeedAlgoOptin_Maker
from gwatn.types import InitialTadeedAlgoTransfer_Maker
from gwatn.types import JoinDispatchContract_Maker
from gwatn.types import LatestPrice_Maker
from gwatn.types import MarketSlot_Maker
from gwatn.types import MarketTypeGt_Maker
from gwatn.types import MultipurposeSensorCacGt_Maker
from gwatn.types import MultipurposeSensorComponentGt_Maker
from gwatn.types import NewTadeedAlgoOptin_Maker
from gwatn.types import NewTadeedSend_Maker
from gwatn.types import OldTadeedAlgoReturn_Maker
from gwatn.types import PipeFlowSensorCacGt_Maker
from gwatn.types import PipeFlowSensorComponentGt_Maker
from gwatn.types import PowerWatts_Maker
from gwatn.types import PriceQuantity_Maker
from gwatn.types import PriceQuantityUnitless_Maker
from gwatn.types import Ready_Maker
from gwatn.types import RelayCacGt_Maker
from gwatn.types import RelayComponentGt_Maker
from gwatn.types import ResistiveHeaterCacGt_Maker
from gwatn.types import ResistiveHeaterComponentGt_Maker
from gwatn.types import ScadaCertTransfer_Maker
from gwatn.types import SimplesimDriverData_Maker
from gwatn.types import SimplesimDriverDataBsh_Maker
from gwatn.types import SimplesimDriverReport_Maker
from gwatn.types import SimplesimSnapshotBrickstorageheater_Maker
from gwatn.types import SimpleTempSensorCacGt_Maker
from gwatn.types import SimpleTempSensorComponentGt_Maker
from gwatn.types import SimTimestep_Maker
from gwatn.types import SlaEnter_Maker
from gwatn.types import SnapshotSpaceheat_Maker
from gwatn.types import SpaceheatNodeGt_Maker
from gwatn.types import SuperStarter_Maker
from gwatn.types import SupervisorContainerGt_Maker
from gwatn.types import TadeedSpecsHack_Maker
from gwatn.types import TavalidatorcertAlgoCreate_Maker
from gwatn.types import TavalidatorcertAlgoTransfer_Maker
from gwatn.types import TelemetryReportingConfig_Maker
from gwatn.types import TelemetrySnapshotSpaceheat_Maker
from gwatn.types import TerminalassetCertifyHack_Maker


TypeMakerByName: Dict[str, HeartbeatA_Maker] = {}


@no_type_check
def type_makers() -> List[HeartbeatA_Maker]:
    return [
        AcceptedBid_Maker,
        AtnBid_Maker,
        AtnParams_Maker,
        AtnParamsBrickstorageheater_Maker,
        AtnParamsReport_Maker,
        BaseGNodeGt_Maker,
        BasegnodeScadaCreate_Maker,
        ComponentAttributeClassGt_Maker,
        ComponentGt_Maker,
        DataChannel_Maker,
        DiscoverycertAlgoCreate_Maker,
        DispatchContractConfirmed_Maker,
        EgaugeIo_Maker,
        EgaugeRegisterConfig_Maker,
        ElectricMeterCacGt_Maker,
        ElectricMeterComponentGt_Maker,
        FloParams_Maker,
        FloParamsBrickstorageheater_Maker,
        FloParamsReport_Maker,
        GNodeGt_Maker,
        GNodeInstanceGt_Maker,
        GtDispatchBoolean_Maker,
        GtDispatchBooleanLocal_Maker,
        GtDriverBooleanactuatorCmd_Maker,
        GtShBooleanactuatorCmdStatus_Maker,
        GtShCliAtnCmd_Maker,
        GtShMultipurposeTelemetryStatus_Maker,
        GtShSimpleTelemetryStatus_Maker,
        GtShStatus_Maker,
        GtShTelemetryFromMultipurposeSensor_Maker,
        GtTelemetry_Maker,
        GwCertId_Maker,
        HeartbeatA_Maker,
        HeartbeatB_Maker,
        InitialTadeedAlgoCreate_Maker,
        InitialTadeedAlgoOptin_Maker,
        InitialTadeedAlgoTransfer_Maker,
        JoinDispatchContract_Maker,
        LatestPrice_Maker,
        MarketSlot_Maker,
        MarketTypeGt_Maker,
        MultipurposeSensorCacGt_Maker,
        MultipurposeSensorComponentGt_Maker,
        NewTadeedAlgoOptin_Maker,
        NewTadeedSend_Maker,
        OldTadeedAlgoReturn_Maker,
        PipeFlowSensorCacGt_Maker,
        PipeFlowSensorComponentGt_Maker,
        PowerWatts_Maker,
        PriceQuantity_Maker,
        PriceQuantityUnitless_Maker,
        Ready_Maker,
        RelayCacGt_Maker,
        RelayComponentGt_Maker,
        ResistiveHeaterCacGt_Maker,
        ResistiveHeaterComponentGt_Maker,
        ScadaCertTransfer_Maker,
        SimTimestep_Maker,
        SimpleTempSensorCacGt_Maker,
        SimpleTempSensorComponentGt_Maker,
        SimplesimDriverData_Maker,
        SimplesimDriverDataBsh_Maker,
        SimplesimDriverReport_Maker,
        SimplesimSnapshotBrickstorageheater_Maker,
        SlaEnter_Maker,
        SnapshotSpaceheat_Maker,
        SpaceheatNodeGt_Maker,
        SuperStarter_Maker,
        SupervisorContainerGt_Maker,
        TadeedSpecsHack_Maker,
        TavalidatorcertAlgoCreate_Maker,
        TavalidatorcertAlgoTransfer_Maker,
        TelemetryReportingConfig_Maker,
        TelemetrySnapshotSpaceheat_Maker,
        TerminalassetCertifyHack_Maker,
    ]


for maker in type_makers():
    TypeMakerByName[maker.type_name] = maker


def version_by_type_name() -> Dict[str, str]:
    """
    Returns:
        Dict[str, str]: Keys are TypeNames, values are versions
    """

    v: Dict[str, str] = {
        "accepted.bid": "000",
        "atn.bid": "001",
        "atn.params": "000",
        "atn.params.brickstorageheater": "000",
        "atn.params.report": "000",
        "base.g.node.gt": "002",
        "basegnode.scada.create": "000",
        "component.attribute.class.gt": "000",
        "component.gt": "000",
        "data.channel": "000",
        "discoverycert.algo.create": "000",
        "dispatch.contract.confirmed": "000",
        "egauge.io": "000",
        "egauge.register.config": "000",
        "electric.meter.cac.gt": "000",
        "electric.meter.component.gt": "000",
        "flo.params": "000",
        "flo.params.brickstorageheater": "000",
        "flo.params.report": "000",
        "g.node.gt": "002",
        "g.node.instance.gt": "000",
        "gt.dispatch.boolean": "110",
        "gt.dispatch.boolean.local": "110",
        "gt.driver.booleanactuator.cmd": "100",
        "gt.sh.booleanactuator.cmd.status": "100",
        "gt.sh.cli.atn.cmd": "110",
        "gt.sh.multipurpose.telemetry.status": "100",
        "gt.sh.simple.telemetry.status": "100",
        "gt.sh.status": "110",
        "gt.sh.telemetry.from.multipurpose.sensor": "100",
        "gt.telemetry": "110",
        "gw.cert.id": "000",
        "heartbeat.a": "100",
        "heartbeat.b": "001",
        "initial.tadeed.algo.create": "000",
        "initial.tadeed.algo.optin": "002",
        "initial.tadeed.algo.transfer": "000",
        "join.dispatch.contract": "000",
        "latest.price": "000",
        "market.slot": "000",
        "market.type.gt": "000",
        "multipurpose.sensor.cac.gt": "000",
        "multipurpose.sensor.component.gt": "000",
        "new.tadeed.algo.optin": "000",
        "new.tadeed.send": "000",
        "old.tadeed.algo.return": "000",
        "pipe.flow.sensor.cac.gt": "000",
        "pipe.flow.sensor.component.gt": "000",
        "power.watts": "000",
        "price.quantity": "000",
        "price.quantity.unitless": "000",
        "ready": "001",
        "relay.cac.gt": "000",
        "relay.component.gt": "000",
        "resistive.heater.cac.gt": "000",
        "resistive.heater.component.gt": "000",
        "scada.cert.transfer": "000",
        "sim.timestep": "000",
        "simple.temp.sensor.cac.gt": "000",
        "simple.temp.sensor.component.gt": "000",
        "simplesim.driver.data": "000",
        "simplesim.driver.data.bsh": "000",
        "simplesim.driver.report": "000",
        "simplesim.snapshot.brickstorageheater": "000",
        "sla.enter": "000",
        "snapshot.spaceheat": "000",
        "spaceheat.node.gt": "100",
        "super.starter": "000",
        "supervisor.container.gt": "000",
        "tadeed.specs.hack": "000",
        "tavalidatorcert.algo.create": "000",
        "tavalidatorcert.algo.transfer": "000",
        "telemetry.reporting.config": "000",
        "telemetry.snapshot.spaceheat": "000",
        "terminalasset.certify.hack": "000",
    }

    return v


def status_by_versioned_type_name() -> Dict[str, str]:
    """
    Returns:
        Dict[str, str]: Keys are versioned TypeNames, values are type status
    """

    v: Dict[str, str] = {
        "accepted.bid.000": "Pending",
        "atn.bid.001": "Pending",
        "atn.params.000": "Active",
        "atn.params.brickstorageheater.000": "Pending",
        "atn.params.report.000": "Active",
        "base.g.node.gt.002": "Active",
        "basegnode.scada.create.000": "Active",
        "component.attribute.class.gt.000": "Active",
        "component.gt.000": "Active",
        "data.channel.000": "Active",
        "discoverycert.algo.create.000": "Active",
        "dispatch.contract.confirmed.000": "Active",
        "egauge.io.000": "Active",
        "egauge.register.config.000": "Active",
        "electric.meter.cac.gt.000": "Active",
        "electric.meter.component.gt.000": "Active",
        "flo.params.000": "Active",
        "flo.params.brickstorageheater.000": "Active",
        "flo.params.report.000": "Pending",
        "g.node.gt.002": "Active",
        "g.node.instance.gt.000": "Active",
        "gt.dispatch.boolean.110": "Active",
        "gt.dispatch.boolean.local.110": "Active",
        "gt.driver.booleanactuator.cmd.100": "Active",
        "gt.sh.booleanactuator.cmd.status.100": "Active",
        "gt.sh.cli.atn.cmd.110": "Active",
        "gt.sh.multipurpose.telemetry.status.100": "Active",
        "gt.sh.simple.telemetry.status.100": "Active",
        "gt.sh.status.110": "Active",
        "gt.sh.telemetry.from.multipurpose.sensor.100": "Active",
        "gt.telemetry.110": "Active",
        "gw.cert.id.000": "Active",
        "heartbeat.a.100": "Active",
        "heartbeat.b.001": "Active",
        "initial.tadeed.algo.create.000": "Active",
        "initial.tadeed.algo.optin.002": "Active",
        "initial.tadeed.algo.transfer.000": "Active",
        "join.dispatch.contract.000": "Active",
        "latest.price.000": "Pending",
        "market.slot.000": "Pending",
        "market.type.gt.000": "Pending",
        "multipurpose.sensor.cac.gt.000": "Active",
        "multipurpose.sensor.component.gt.000": "Active",
        "new.tadeed.algo.optin.000": "Active",
        "new.tadeed.send.000": "Active",
        "old.tadeed.algo.return.000": "Active",
        "pipe.flow.sensor.cac.gt.000": "Active",
        "pipe.flow.sensor.component.gt.000": "Active",
        "power.watts.000": "Active",
        "price.quantity.000": "Pending",
        "price.quantity.unitless.000": "Pending",
        "ready.001": "Active",
        "relay.cac.gt.000": "Active",
        "relay.component.gt.000": "Active",
        "resistive.heater.cac.gt.000": "Active",
        "resistive.heater.component.gt.000": "Active",
        "scada.cert.transfer.000": "Pending",
        "sim.timestep.000": "Active",
        "simple.temp.sensor.cac.gt.000": "Active",
        "simple.temp.sensor.component.gt.000": "Active",
        "simplesim.driver.data.000": "Pending",
        "simplesim.driver.data.bsh.000": "Pending",
        "simplesim.driver.report.000": "Pending",
        "simplesim.snapshot.brickstorageheater.000": "Pending",
        "sla.enter.000": "Pending",
        "snapshot.spaceheat.000": "Active",
        "spaceheat.node.gt.100": "Active",
        "super.starter.000": "Active",
        "supervisor.container.gt.000": "Active",
        "tadeed.specs.hack.000": "Pending",
        "tavalidatorcert.algo.create.000": "Active",
        "tavalidatorcert.algo.transfer.000": "Active",
        "telemetry.reporting.config.000": "Active",
        "telemetry.snapshot.spaceheat.000": "Active",
        "terminalasset.certify.hack.000": "Pending",
    }

    return v
