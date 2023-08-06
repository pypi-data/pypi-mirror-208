""" WeatherSource Class Definition """
from abc import ABC
from typing import Optional


class WeatherSource(ABC):
    by_id = {}

    base_props = []
    base_props.append("alias")
    base_props.append("description")
    base_props.append("url")
    base_props.append("contact_email")
    base_props.append("color_hex")

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
        description: Optional[str] = None,
        url: Optional[str] = None,
        contact_email: Optional[str] = None,
        color_hex: Optional[str] = None,
    ):
        self.alias = alias
        self.description = description
        self.url = url
        self.contact_email = contact_email
        self.color_hex = color_hex


PlatformWeatherSource = {}


"""NOAA_LCD
"""
NOAA_LCD = WeatherSource(
    alias="noaa.lcd",
    description="Local Climate Data emailed from NOA via this url, using WeatherLocationAlias zip code",
    url="https://www.ncdc.noaa.gov/cdo-web/datatools/lcd",
    contact_email="",
    color_hex="#0e6f05",
)

PlatformWeatherSource[NOAA_LCD.alias] = NOAA_LCD


"""US_NWS
"""
US_NWS = WeatherSource(
    alias="us.nws",
    description="Weather data from the national weather service api",
    url="https://api.weather.gov",
    contact_email="",
    color_hex="",
)

PlatformWeatherSource[US_NWS.alias] = US_NWS


"""PVWATTS
"""
PVWATTS = WeatherSource(
    alias="pvwatts",
    description="Clear Sky Plane of Array Irradiance data available from NREL in a PV calculator at this URL.",
    url="https://pvwatts.nrel.gov/",
    contact_email="",
    color_hex="#438a79",
)

PlatformWeatherSource[PVWATTS.alias] = PVWATTS


"""GW"""
GW = WeatherSource(
    alias="gw",
    description="Data manufactured by GridWorks",
    url="",
    contact_email="gbaker@gridworks-consulting.com",
    color_hex="",
)


PlatformWeatherSource[GW.alias] = GW
