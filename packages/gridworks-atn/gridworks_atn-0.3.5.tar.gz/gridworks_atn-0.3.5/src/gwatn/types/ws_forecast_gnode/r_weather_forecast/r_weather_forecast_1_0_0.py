"""MessageMaker for r.weather.forecast.1_0_0"""

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
from gwatn.types.ws_forecast_gnode.r_weather_forecast.r_weather_forecast_1_0_0_payload import (
    Payload,
)


class R_Weather_Forecast_1_0_0(HackTypeBase):
    mp_alias = "r.weather.forecast.1_0_0"
    routing_key_base = "ws.forecast.gnode"

    @classmethod
    def create_payload_from_camel_dict(cls, d: dict) -> Payload:
        if "MpAlias" not in d.keys():
            d["MpAlias"] = "r.weather.forecast.1_0_0"
        if "SkyClarityMethodAlias" not in d.keys():
            d["SkyClarityMethodAlias"] = None
        if "IrradianceType" not in d.keys():
            d["IrradianceType"] = None
        if "IrradianceSourceAlias" not in d.keys():
            d["IrradianceSourceAlias"] = None
        if "TempMethodAlias" not in d.keys():
            d["TempMethodAlias"] = None
        if "TempSourceAlias" not in d.keys():
            d["TempSourceAlias"] = None
        if "OpaqueCloudCoveragePercents" not in d.keys():
            d["OpaqueCloudCoveragePercents"] = None
        if "IrradianceWPerM2" not in d.keys():
            d["IrradianceWPerM2"] = None
        if "TempUnit" not in d.keys():
            d["TempUnit"] = None
        if "IrlTimeUtc" not in d.keys():
            d["IrlTimeUtc"] = None
        if "SkyClaritySourceAlias" not in d.keys():
            d["SkyClaritySourceAlias"] = None
        if "IrradianceMethodAlias" not in d.keys():
            d["IrradianceMethodAlias"] = None
        if "Temperatures" not in d.keys():
            d["Temperatures"] = None
        list_as_floats = []
        if not isinstance(d["Temperatures"], list):
            raise SchemaError('d["Temperatures"] must be a list!!')
        for elt in d["Temperatures"]:
            try:
                list_as_floats.append(float(elt))
            except ValueError:
                pass  # This will get caught in is_valid() check below
        d["Temperatures"] = list_as_floats
        if "WorldInstanceAlias" not in d.keys():
            d["WorldInstanceAlias"] = None
        p = Payload(
            MpAlias=d["MpAlias"],
            StartYearUtc=d["StartYearUtc"],
            SkyClarityMethodAlias=d["SkyClarityMethodAlias"],
            WeatherUid=d["WeatherUid"],
            StartMonthUtc=d["StartMonthUtc"],
            IrradianceType=d["IrradianceType"],
            IrradianceSourceAlias=d["IrradianceSourceAlias"],
            FromGNodeInstanceId=d["FromGNodeInstanceId"],
            TempMethodAlias=d["TempMethodAlias"],
            TempSourceAlias=d["TempSourceAlias"],
            StartDayUtc=d["StartDayUtc"],
            StartHourUtc=d["StartHourUtc"],
            ForecastUnixTimeS=d["ForecastUnixTimeS"],
            OpaqueCloudCoveragePercents=d["OpaqueCloudCoveragePercents"],
            IrradianceWPerM2=d["IrradianceWPerM2"],
            StartMinuteUtc=d["StartMinuteUtc"],
            MessageId=d["MessageId"],
            TempUnit=d["TempUnit"],
            SliceDurationMinutes=d["SliceDurationMinutes"],
            IrlTimeUtc=d["IrlTimeUtc"],
            SkyClaritySourceAlias=d["SkyClaritySourceAlias"],
            FromGNodeAlias=d["FromGNodeAlias"],
            Comment=d["Comment"],
            TimezoneString=d["TimezoneString"],
            LocationAlias=d["LocationAlias"],
            IrradianceMethodAlias=d["IrradianceMethodAlias"],
            Temperatures=d["Temperatures"],
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
        start_utc: datetime.datetime,
        weather_uid: str,
        forecast_unix_time_s: int,
        comment: str,
        timezone_string: str,
        location_alias: str,
        slice_duration_minutes: List[int],
        irradiance_type=RecognizedIrradianceType.PlaneOfArray.value,
        sky_clarity_method_alias: Optional[str] = None,
        irradiance_source_alias: Optional[str] = None,
        temp_method_alias: Optional[str] = None,
        temp_source_alias: Optional[str] = None,
        temp_unit: Optional[str] = None,
        irl_time_utc: Optional[str] = None,
        sky_clarity_source_alias: Optional[str] = None,
        irradiance_method_alias: Optional[str] = None,
        opaque_cloud_coverage_percents: Optional[List[int]] = None,
        irradiance_w_per_m2: Optional[List[int]] = None,
        temperatures: Optional[List[float]] = None,
    ):
        super().__init__(routing_key_base="ws.forecast.gnode", agent=agent)
        self.errors = []
        self.payload = None
        if agent is None:
            raise Exception(
                f"Message protocol {R_Weather_Forecast_1_0_0.mp_alias} must be generated by a message agent"
            )
        if agent == test_dummy.TEST_DUMMY_AGENT:
            from_g_node_alias = test_dummy.TEST_DUMMY_G_NODE_ALIAS
            from_g_node_instance_id = test_dummy.TEST_DUMMY_G_NODE_INSTANCE_ID
            world_instance_alias = test_dummy.TEST_DUMMY_WORLD_INSTANCE_ALIAS
            irl_time_utc = log_style_utc_date_w_millis(time.time())
        else:
            if not agent.gni.g_node.is_ws:
                raise Exception(
                    f"Message protocol {R_Weather_Forecast_1_0_0.mp_alias} must come from a Ws"
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
        if not isinstance(temperatures, list):
            raise SchemaError(f"temperatures must be a list!!")
        try:
            tmp_temperatures = []
            for elt in temperatures:
                tmp_temperatures.append(float(elt))
            temperatures = tmp_temperatures
        except ValueError:
            pass  # This will get caught in is_valid() check below

        p = Payload(
            MpAlias=R_Weather_Forecast_1_0_0.mp_alias,
            WorldInstanceAlias=world_instance_alias,
            FromGNodeAlias=from_g_node_alias,
            FromGNodeInstanceId=from_g_node_instance_id,
            StartYearUtc=start_utc.year,
            SkyClarityMethodAlias=sky_clarity_method_alias,
            WeatherUid=weather_uid,
            StartMonthUtc=start_utc.month,
            IrradianceType=irradiance_type,
            IrradianceSourceAlias=irradiance_source_alias,
            TempMethodAlias=temp_method_alias,
            TempSourceAlias=temp_source_alias,
            StartDayUtc=start_utc.day,
            StartHourUtc=start_utc.hour,
            ForecastUnixTimeS=forecast_unix_time_s,
            OpaqueCloudCoveragePercents=opaque_cloud_coverage_percents,
            IrradianceWPerM2=irradiance_w_per_m2,
            StartMinuteUtc=start_utc.minute,
            TempUnit=temp_unit,
            SliceDurationMinutes=slice_duration_minutes,
            IrlTimeUtc=irl_time_utc,
            SkyClaritySourceAlias=sky_clarity_source_alias,
            Comment=comment,
            TimezoneString=timezone_string,
            LocationAlias=location_alias,
            IrradianceMethodAlias=irradiance_method_alias,
            Temperatures=temperatures,
            MessageId=str(uuid.uuid4()),
        )

        is_valid, errors = p.is_valid()
        if is_valid is False:
            raise SchemaError(f"Failed to create payload due to these errors: {errors}")
        self.payload = p
