""" PriceMethod Class Definition """
from abc import ABC
from typing import Dict
from typing import Optional


class PriceMethod(ABC):
    by_id = {}
    by_alias = {}
    base_props = []
    base_props.append("alias")
    base_props.append("contact_email")
    base_props.append("color_hex")
    base_props.append("url")

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
        contact_email: Optional[str] = None,
        color_hex: Optional[str] = None,
        url: Optional[str] = None,
    ):
        self.alias = alias
        self.contact_email = contact_email
        self.color_hex = color_hex
        self.url = url
        self.__class__.by_alias[self.alias] = self


PlatformPriceMethod: Dict[str, PriceMethod] = {}


"""ERCOT_RTM60_APIZIP: ERCOT API zip for 60 minute real time prices
"""
ERCOT_RTM60_APIZIP = PriceMethod(alias="ercot.rtm60.apizip")

PlatformPriceMethod[ERCOT_RTM60_APIZIP.alias] = ERCOT_RTM60_APIZIP


"""CAISOENERGYONLINE_FROM5MIN_DUBIOUS: Data cleaning etc done by hand in a dubious way. Do not trust completely.
"""
CAISOENERGYONLINE_FROM5MIN_DUBIOUS = PriceMethod(
    alias="caisoenergyonline.from5min.dubious",
    contact_email="gbaker@gridworks-consulting.com",
    color_hex="#438a79",
    url="<![CDATA[http://www.energyonline.com/Data/GenericData.aspx?DataId=19&CAISO___Real-time_Price]]>",
)

PlatformPriceMethod[
    CAISOENERGYONLINE_FROM5MIN_DUBIOUS.alias
] = CAISOENERGYONLINE_FROM5MIN_DUBIOUS


"""GW_STDEV_UP200: Average price held constant and standard deviation increased by 200 percent
        from source pointed to in comment. Add difference between price and mean
        to each price.
"""
GW_STDEV_UP200 = PriceMethod(
    alias="gw.stdev.up200",
    contact_email="gbaker@gridworks-consulting.com",
    color_hex="#7b47d6",
)

PlatformPriceMethod[GW_STDEV_UP200.alias] = GW_STDEV_UP200


"""GW_UP50: All prices increased by 50 precent from source pointed to in comment
"""
GW_UP50 = PriceMethod(alias="gw.up50", contact_email="gbaker@gridworks-consulting.com")

PlatformPriceMethod[GW_UP50.alias] = GW_UP50


"""ISONEEXPRESS_DA_WEB
"""
ISONEEXPRESS_DA_WEB = PriceMethod(
    alias="isoneexpress.da.web",
    url="https://www.iso-ne.com/isoexpress/web/reports/pricing/-/tree/lmp-by-node",
)

PlatformPriceMethod[ISONEEXPRESS_DA_WEB.alias] = ISONEEXPRESS_DA_WEB


"""ISONEEXPRESS_REG_5MINFINALRCP_HRLYAVG_WEB
"""
ISONEEXPRESS_REG_5MINFINALRCP_HRLYAVG_WEB = PriceMethod(
    alias="isoneexpress.reg.5minfinalrcp.hrlyavg.web",
    url="https://www.iso-ne.com/isoexpress/web/reports/pricing/-/tree/lmp-by-node",
)

PlatformPriceMethod[
    ISONEEXPRESS_REG_5MINFINALRCP_HRLYAVG_WEB.alias
] = ISONEEXPRESS_REG_5MINFINALRCP_HRLYAVG_WEB


"""GW_CA_RCEA_OFFPEAK1
"""
GW_CA_RCEA_OFFPEAK1 = PriceMethod(
    alias="gw.ca.rcea.offpeak1",
    contact_email="gbaker@gridworks-consulting.com",
    color_hex="#285248",
)

PlatformPriceMethod[GW_CA_RCEA_OFFPEAK1.alias] = GW_CA_RCEA_OFFPEAK1


"""GW_CA_RCEA_ONEPRICE
"""
GW_CA_RCEA_ONEPRICE = PriceMethod(
    alias="gw.ca.rcea.oneprice",
    contact_email="gbaker@gridworks-consulting.com",
    color_hex="#E3E83F ",
)

PlatformPriceMethod[GW_CA_RCEA_ONEPRICE.alias] = GW_CA_RCEA_ONEPRICE


"""GW_ME_VERSANT_A1_RES_ETS: Versant Power Residential Electric Thermal Storage Service Rate Time-of-Use
"""
GW_ME_VERSANT_A1_RES_ETS = PriceMethod(
    alias="gw.me.versant.a1.res.ets",
    contact_email="gbaker@gridworks-consulting.com",
    color_hex="https://www.versantpower.com/media/49248/Rate_A1_ResETS.pdf",
)

PlatformPriceMethod[GW_ME_VERSANT_A1_RES_ETS.alias] = GW_ME_VERSANT_A1_RES_ETS


"""GAIA_ERCOT_RT_ALPHA: Machine learning based regression model to predict RTM prices by minimizing
        the mean squared errors. Two hours of 15-minute RTM market forecasts followed
        by day ahead.
"""
GAIA_ERCOT_RT_ALPHA = PriceMethod(
    alias="gaia.ercot.rt.alpha",
    contact_email="vivek@gaia-scope.com",
    color_hex="#33D7FF",
)

PlatformPriceMethod[GAIA_ERCOT_RT_ALPHA.alias] = GAIA_ERCOT_RT_ALPHA


"""GW_PATHWAYS_ALPHA: Take local prices and adjust it to match Analysis Group carbon pricing
        distribution. First pass by George.
"""
GW_PATHWAYS_ALPHA = PriceMethod(
    alias="gw.pathways.alpha",
    contact_email="gbaker@gridworks-consulting.com",
    color_hex="#912683",
)

PlatformPriceMethod[GW_PATHWAYS_ALPHA.alias] = GW_PATHWAYS_ALPHA


"""GW_RT_PERFECTFORESIGHT: Perfect foresight for realtime prices.
"""
GW_RT_PERFECTFORESIGHT = PriceMethod(
    alias="gw.rt.perfectforesight", contact_email="jmillar@gridworks-consulting.com"
)

PlatformPriceMethod[GW_RT_PERFECTFORESIGHT.alias] = GW_RT_PERFECTFORESIGHT


"""ISONEEXPRESS_FINALRT_HR_WEB: Final hourly realtime energy prices scraped from isone isoexpress
"""
ISONEEXPRESS_FINALRT_HR_WEB = PriceMethod(
    alias="isoneexpress.finalrt.hr.web",
    url="https://www.iso-ne.com/isoexpress/web/reports/pricing/-/tree/lmp-by-node",
)

PlatformPriceMethod[ISONEEXPRESS_FINALRT_HR_WEB.alias] = ISONEEXPRESS_FINALRT_HR_WEB


"""ERCOT_RTM15_APIZIP: ERCOT API zip for 15 minute real time prices
"""
ERCOT_RTM15_APIZIP = PriceMethod(alias="ercot.rtm15.apizip")

PlatformPriceMethod[ERCOT_RTM15_APIZIP.alias] = ERCOT_RTM15_APIZIP


"""GW_RTFROMDA_ALPHA: Use the most recent da prices, then repeating the latest da prices. Assumes
        tomorrow's prices (starting at midnight local time) are available at a
        DA posting time specific to that DA market.
"""
GW_RTFROMDA_ALPHA = PriceMethod(
    alias="gw.rtfromda.alpha", contact_email="jmillar@gridworks-consulting.com"
)

PlatformPriceMethod[GW_RTFROMDA_ALPHA.alias] = GW_RTFROMDA_ALPHA


"""EPEXSPOT_WEB: National Grid prices from epex website, only available for a couple days.
"""
EPEXSPOT_WEB = PriceMethod(
    alias="epexspot.web",
    contact_email="gbaker@gridworks-consulting.com",
    color_hex="#10201C",
    url="<![CDATA[https://www.epexspot.com/en/market-data?market_area=GB&delivery_date=2021-10-08&underlying_year=&modality=Continuous&sub_modality=&product=30&data_mode=table&period=]]>",
)

PlatformPriceMethod[EPEXSPOT_WEB.alias] = EPEXSPOT_WEB


"""ISONEEXPRESS_GRABREAL_FINALRT_HR_WEB: Final hourly realtime energy prices scraped from isone isoexpress, swapping
        world root for w
"""
ISONEEXPRESS_GRABREAL_FINALRT_HR_WEB = PriceMethod(
    alias="isoneexpress.grabreal.finalrt.hr.web",
    url="https://www.iso-ne.com/isoexpress/web/reports/pricing/-/tree/lmp-by-node",
)

PlatformPriceMethod[
    ISONEEXPRESS_GRABREAL_FINALRT_HR_WEB.alias
] = ISONEEXPRESS_GRABREAL_FINALRT_HR_WEB


"""GW_DA_PREDICTED_ROLLING4WKS_ALPHA: Prediction of next period's LMP (electricity price) based on next period's
        day ahead and this period's real-time price done on a rolling 4 weeks continuously
        updating prediction parameters
"""
GW_DA_PREDICTED_ROLLING4WKS_ALPHA = PriceMethod(
    alias="gw.da.predicted.rolling4wks.alpha",
    contact_email="gbaker@gridworks-consulting.com",
    color_hex="#0e6f05",
)

PlatformPriceMethod[
    GW_DA_PREDICTED_ROLLING4WKS_ALPHA.alias
] = GW_DA_PREDICTED_ROLLING4WKS_ALPHA


"""GW_RTFROMDA_PERFECTFORESIGHT: Use perfect DA foresight for RT prediction.
"""
GW_RTFROMDA_PERFECTFORESIGHT = PriceMethod(
    alias="gw.rtfromda.perfectforesight",
    contact_email="gbaker@gridworks-consulting.com",
)

PlatformPriceMethod[GW_RTFROMDA_PERFECTFORESIGHT.alias] = GW_RTFROMDA_PERFECTFORESIGHT


"""GW_PERFECTRTFOR2_THEN_DA: Perfect foresight for realtime prices for 2 hours, then the latest available
        day ahead prices.
"""
GW_PERFECTRTFOR2_THEN_DA = PriceMethod(
    alias="gw.perfectrtfor2.then.da", contact_email="jmillar@gridworks-consulting.com"
)

PlatformPriceMethod[GW_PERFECTRTFOR2_THEN_DA.alias] = GW_PERFECTRTFOR2_THEN_DA


"""GW_PERFECTRTFOR12_THEN_DA: Perfect foresight for realtime prices for 12 hours, then the latest available
        day ahead prices.
"""
GW_PERFECTRTFOR12_THEN_DA = PriceMethod(
    alias="gw.perfectrtfor12.then.da", contact_email="jmillar@gridworks-consulting.com"
)

PlatformPriceMethod[GW_PERFECTRTFOR12_THEN_DA.alias] = GW_PERFECTRTFOR12_THEN_DA


"""GAIA_ERCOT_RT_BETA
"""
GAIA_ERCOT_RT_BETA = PriceMethod(alias="gaia.ercot.rt.beta")

PlatformPriceMethod[GAIA_ERCOT_RT_BETA.alias] = GAIA_ERCOT_RT_BETA


"""ERCOT_DAM60_APIZIP: ERCOT API zip for day ahead hourly prices
"""
ERCOT_DAM60_APIZIP = PriceMethod(alias="ercot.dam60.apizip")

PlatformPriceMethod[ERCOT_DAM60_APIZIP.alias] = ERCOT_DAM60_APIZIP
