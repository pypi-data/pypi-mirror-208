import enum


class WeatherSource(enum.Enum):
    PVWATTS = "pvwatts"
    NOAA_LCD = "noaa.lcd"
    GW = "gw"
    US_NWS = "us.nws"
