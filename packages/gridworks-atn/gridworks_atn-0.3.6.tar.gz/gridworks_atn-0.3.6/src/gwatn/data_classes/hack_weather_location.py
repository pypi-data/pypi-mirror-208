""" WeatherLocation Class Definition """
import math
from abc import ABC
from typing import Dict
from typing import Optional

import numpy as np


EARTH_RADIUS_KM = 6371.0


class WeatherLocation(ABC):
    by_id = {}

    base_props = []
    base_props.append("alias")
    base_props.append("lat")
    base_props.append("lon")
    base_props.append("timezone_string")
    base_props.append("state_usps")
    base_props.append("postal_code")
    base_props.append("noaa_cdo_id")
    base_props.append("nws_grid_x")
    base_props.append("nws_grid_y")
    base_props.append("nws_wfo_abbr")

    def __new__(cls, alias, *args, **kwargs):
        try:
            return cls.by_id[alias]
        except KeyError:
            instance = super().__new__(cls)
            cls.by_id[alias] = instance
            return instance

    def __init__(
        self,
        alias: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        timezone_string: Optional[str] = None,
        state_usps: Optional[str] = None,
        postal_code: Optional[str] = None,
        noaa_cdo_id: Optional[str] = None,
        nws_grid_x: Optional[int] = None,
        nws_grid_y: Optional[int] = None,
        nws_wfo_abbr: Optional[str] = None,
    ):
        self.alias = alias
        self.lat = lat
        self.lon = lon
        self.timezone_string = timezone_string
        self.state_usps = state_usps
        self.postal_code = postal_code
        self.noaa_cdo_id = noaa_cdo_id
        self.nws_grid_x = nws_grid_x
        self.nws_grid_y = nws_grid_y
        self.nws_wfo_abbr = nws_wfo_abbr


WS_US_CA_HMBLT_ARCATA = WeatherLocation(
    alias="ws.us.ca.hmblt.arcata",
    lat=40.9523,
    lon=-124.0749,
    timezone_string="US/Pacific",
    state_usps="ca",
    postal_code="95519",
    noaa_cdo_id="WBAN:24283",
    nws_grid_x=65,
    nws_grid_y=113,
    nws_wfo_abbr="EKA",
)


WS_US_CA_HMBLT_EUREKA = WeatherLocation(
    alias="ws.us.ca.hmblt.eureka",
    lat=40.7223,
    lon=-124.1974,
    timezone_string="US/Pacific",
    state_usps="ca",
    postal_code="95503",
    noaa_cdo_id="WBAN:24283",
    nws_grid_x=60,
    nws_grid_y=104,
    nws_wfo_abbr="EKA",
)


"""WS_US_ME_HOULTONAIRPORT"""
WS_US_ME_HOULTONAIRPORT = WeatherLocation(
    alias="ws.us.me.houltonairport",
    lat=46.13077,
    lon=-67.80476,
    timezone_string="US/Eastern",
    state_usps="me",
    postal_code="04730",
    noaa_cdo_id="WBAN:14609",
    nws_grid_x=90,
    nws_grid_y=129,
    nws_wfo_abbr="CAR",
)


"""WS_US_ME_MILLINOCKETAIRPORT"""
WS_US_ME_MILLINOCKETAIRPORT = WeatherLocation(
    alias="ws.us.me.millinocketairport",
    lat=45.65,
    lon=-68.7,
    timezone_string="US/Eastern",
    state_usps="me",
    postal_code="04462",
    noaa_cdo_id="WBAN:14610",
    nws_grid_x=66,
    nws_grid_y=102,
    nws_wfo_abbr="CAR",
)

WS_US_NH_WALPOLE = WeatherLocation(
    alias="ws.us.nh.walpole",
    lat=43.07834,
    lon=-72.4248,
    timezone_string="US/Eastern",
    state_usps="nh",
    postal_code="03608",
    nws_grid_x=14,
    nws_grid_y=22,
    nws_wfo_abbr="GYX",
)


def WsLocation() -> Dict[str, WeatherLocation]:
    d = {}
    d[WS_US_ME_HOULTONAIRPORT.alias] = WS_US_ME_HOULTONAIRPORT
    d[WS_US_ME_MILLINOCKETAIRPORT.alias] = WS_US_ME_MILLINOCKETAIRPORT
    d[WS_US_CA_HMBLT_ARCATA.alias] = WS_US_CA_HMBLT_ARCATA
    d[WS_US_CA_HMBLT_EUREKA.alias] = WS_US_CA_HMBLT_EUREKA
    d[WS_US_NH_WALPOLE.alias] = WS_US_NH_WALPOLE
    return d


def weather_location_distance_km(wl1: WeatherLocation, wl2: WeatherLocation):
    # Uses the Haversine formula, which takes curvature of earth into consideration
    lat1 = math.radians(wl1.lat)
    lon1 = math.radians(wl1.lon)
    lat2 = math.radians(wl2.lat)
    lon2 = math.radians(wl2.lon)
    delta_lon = lon2 - lon1
    delta_lat = lat2 - lat1
    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance_km = EARTH_RADIUS_KM * c
    return round(distance_km, 2)
