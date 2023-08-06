"""MessageMaker for r.weather.forecast.raw.1_0_0"""

import datetime
import time
import uuid
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import gwatn.types.hack_test_dummy as test_dummy
from gwatn.enums import RecognizedIrradianceType
from gwatn.errors import *
from gwatn.types.hack_type_base import HackTypeBase
from gwatn.types.hack_utils import log_style_utc_date_w_millis
from gwatn.types.ws_forecast_gnode.r_weather_forecast_raw.r_weather_forecast_raw_1_0_0_payload import (
    Payload,
)


class R_Weather_Forecast_Raw_1_0_0(HackTypeBase):
    mp_alias = "r.weather.forecast.raw.1_0_0"
    routing_key_base = "ws.forecast.gnode"

    @classmethod
    def create_payload_from_camel_dict(cls, d: dict) -> Payload:
        if "MpAlias" not in d.keys():
            d["MpAlias"] = "r.weather.forecast.raw.1_0_0"
        if "TempSourceAlias" not in d.keys():
            d["TempSourceAlias"] = None
        if "SkyClarityMethodAlias" not in d.keys():
            d["SkyClarityMethodAlias"] = None
        if "TempUnit" not in d.keys():
            d["TempUnit"] = None
        if "TempMethodAlias" not in d.keys():
            d["TempMethodAlias"] = None
        if "IrradianceMethodAlias" not in d.keys():
            d["IrradianceMethodAlias"] = None
        if "Temperatures" not in d.keys():
            d["Temperatures"] = None
        if "IrradianceType" not in d.keys():
            d["IrradianceType"] = None
        if "SkyClaritySourceAlias" not in d.keys():
            d["SkyClaritySourceAlias"] = None
        if "IrradianceSourceAlias" not in d.keys():
            d["IrradianceSourceAlias"] = None
        if "OpaqueCloudCoveragePercents" not in d.keys():
            d["OpaqueCloudCoveragePercents"] = None
        if "IrradianceWPerM2" not in d.keys():
            d["IrradianceWPerM2"] = None
        if "IrlTimeUtc" not in d.keys():
            d["IrlTimeUtc"] = None
        if "WorldInstanceAlias" not in d.keys():
            d["WorldInstanceAlias"] = None
        p = Payload(
            MpAlias=d["MpAlias"],
            WeatherUid=d["WeatherUid"],
            TempSourceAlias=d["TempSourceAlias"],
            StartDayUtc=d["StartDayUtc"],
            ForecastUnixTimeS=d["ForecastUnixTimeS"],
            SkyClarityMethodAlias=d["SkyClarityMethodAlias"],
            TempUnit=d["TempUnit"],
            Comment=d["Comment"],
            FromGNodeAlias=d["FromGNodeAlias"],
            StartMonthUtc=d["StartMonthUtc"],
            StartHourUtc=d["StartHourUtc"],
            TempMethodAlias=d["TempMethodAlias"],
            MessageId=d["MessageId"],
            IrradianceMethodAlias=d["IrradianceMethodAlias"],
            FromGNodeInstanceId=d["FromGNodeInstanceId"],
            UniformSliceDurationHrs=float(d["UniformSliceDurationHrs"]),
            StartYearUtc=d["StartYearUtc"],
            TimezoneString=d["TimezoneString"],
            Temperatures=d["Temperatures"],
            IrradianceType=d["IrradianceType"],
            SkyClaritySourceAlias=d["SkyClaritySourceAlias"],
            LocationAlias=d["LocationAlias"],
            IrradianceSourceAlias=d["IrradianceSourceAlias"],
            OpaqueCloudCoveragePercents=d["OpaqueCloudCoveragePercents"],
            IrradianceWPerM2=d["IrradianceWPerM2"],
            IrlTimeUtc=d["IrlTimeUtc"],
            WorldInstanceAlias=d["WorldInstanceAlias"],
        )
        is_valid, errors = p.is_valid()
        if not is_valid:
            raise SchemaError(errors)
        return p

    @classmethod
    def payload_is_valid(
        cls, payload_as_dict: Dict[str, Any]
    ) -> Tuple[bool, Optional[List[str]]]:
        try:
            p = cls.create_payload_from_camel_dict(payload_as_dict)
        except SchemaError as e:
            errors = [e]
            return False, errors
        return p.is_valid()

    def __init__(
        self,
        agent,
        weather_uid: str,
        forecast_unix_time_s: int,
        comment: str,
        uniform_slice_duration_hrs: float,
        start_utc: datetime.datetime,
        timezone_string: str,
        location_alias: str,
        irradiance_type=RecognizedIrradianceType.PlaneOfArray.value,
        temp_source_alias: Optional[str] = None,
        sky_clarity_method_alias: Optional[str] = None,
        temp_unit: Optional[str] = None,
        temp_method_alias: Optional[str] = None,
        irradiance_method_alias: Optional[str] = None,
        sky_clarity_source_alias: Optional[str] = None,
        irradiance_source_alias: Optional[str] = None,
        irl_time_utc: Optional[str] = None,
        temperatures: Optional[List[int]] = None,
        opaque_cloud_coverage_percents: Optional[List[int]] = None,
        irradiance_w_per_m2: Optional[List[int]] = None,
    ):
        super().__init__(routing_key_base="ws.forecast.gnode", agent=agent)
        self.errors = []
        self.payload = None
        if agent is None:
            raise Exception(
                f"Message protocol {R_Weather_Forecast_Raw_1_0_0.mp_alias} must be generated by a message agent"
            )
        if agent == test_dummy.TEST_DUMMY_AGENT:
            from_g_node_alias = test_dummy.TEST_DUMMY_G_NODE_ALIAS
            from_g_node_instance_id = test_dummy.TEST_DUMMY_G_NODE_INSTANCE_ID
            world_instance_alias = test_dummy.TEST_DUMMY_WORLD_INSTANCE_ALIAS
            irl_time_utc = log_style_utc_date_w_millis(time.time())
        else:
            if not agent.gni.g_node.is_ws:
                raise Exception(
                    f"Message protocol {R_Weather_Forecast_Raw_1_0_0.mp_alias} must come from a Ws"
                )
            from_g_node_alias = agent.gni.g_node.alias
            from_g_node_instance_id = agent.gni.g_node_instance_id
            if agent.world_instance.is_simulated:
                world_instance_alias = agent.world_instance.alias
            else:
                world_instance_alias = None
            if agent.is_debug_mode:
                irl_time_utc = log_style_utc_date_w_millis(time.time())
            else:
                irl_time_utc = None
        try:
            uniform_slice_duration_hrs = float(uniform_slice_duration_hrs)
        except ValueError:
            pass  # This will get caught in is_valid() check below

        p = Payload(
            MpAlias=R_Weather_Forecast_Raw_1_0_0.mp_alias,
            WorldInstanceAlias=world_instance_alias,
            FromGNodeAlias=from_g_node_alias,
            FromGNodeInstanceId=from_g_node_instance_id,
            WeatherUid=weather_uid,
            TempSourceAlias=temp_source_alias,
            StartDayUtc=start_utc.day,
            ForecastUnixTimeS=forecast_unix_time_s,
            SkyClarityMethodAlias=sky_clarity_method_alias,
            TempUnit=temp_unit,
            Comment=comment,
            StartMonthUtc=start_utc.month,
            StartHourUtc=start_utc.hour,
            TempMethodAlias=temp_method_alias,
            IrradianceMethodAlias=irradiance_method_alias,
            UniformSliceDurationHrs=uniform_slice_duration_hrs,
            StartYearUtc=start_utc.year,
            TimezoneString=timezone_string,
            Temperatures=temperatures,
            IrradianceType=irradiance_type,
            SkyClaritySourceAlias=sky_clarity_source_alias,
            LocationAlias=location_alias,
            IrradianceSourceAlias=irradiance_source_alias,
            OpaqueCloudCoveragePercents=opaque_cloud_coverage_percents,
            IrradianceWPerM2=irradiance_w_per_m2,
            IrlTimeUtc=irl_time_utc,
            MessageId=str(uuid.uuid4()),
        )

        is_valid, errors = p.is_valid()
        if is_valid is False:
            raise SchemaError(f"Failed to create payload due to these errors: {errors}")
        self.payload = p
