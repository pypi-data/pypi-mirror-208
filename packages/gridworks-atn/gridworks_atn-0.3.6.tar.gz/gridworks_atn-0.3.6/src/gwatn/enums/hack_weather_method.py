import enum


class WeatherMethod(enum.Enum):
    API_WEATHER_GOV_HOURLY_FORECAST_GRIDPOINT = (
        "api.weather.gov.hourly.forecast.gridpoint"
    )
    FAKE = "fake"
    PVWATTS_POA_MONTH_DAY_ALPHA = "pvwatts.poa.month.day.alpha"
    NOAA_LCD_BASICTEMPGRAB = "noaa.lcd.basictempgrab"
    WEB_SCRAPING = "web.scraping"
    PVWATTS_POA_MONTH_DAY_BETA = "pvwatts.poa.month.day.beta"
    NOAA_LCD_HSC_BETA = "noaa.lcd.hsc.beta"
    SINGLEYEAR_NOAA_LCD_BASICTEMPGRAB = "singleyear.noaa.lcd.basictempgrab"
    NOAA_LCD_HSC_ALPHA = "noaa.lcd.hsc.alpha"
    PREV_YEAR_HACK = "prev.year.hack"
