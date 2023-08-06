import enum


class PriceMethod(enum.Enum):
    ERCOT_RTM60_APIZIP = "ercot.rtm60.apizip"
    CAISOENERGYONLINE_FROM5MIN_DUBIOUS = "caisoenergyonline.from5min.dubious"
    GW_STDEV_UP200 = "gw.stdev.up200"
    GW_UP50 = "gw.up50"
    ISONEEXPRESS_DA_WEB = "isoneexpress.da.web"
    ISONEEXPRESS_REG_5MINFINALRCP_HRLYAVG_WEB = (
        "isoneexpress.reg.5minfinalrcp.hrlyavg.web"
    )
    GW_CA_RCEA_OFFPEAK1 = "gw.ca.rcea.offpeak1"
    GW_CA_RCEA_ONEPRICE = "gw.ca.rcea.oneprice"
    GW_ME_VERSANT_A1_RES_ETS = "gw.me.versant.a1.res.ets"
    GAIA_ERCOT_RT_ALPHA = "gaia.ercot.rt.alpha"
    GW_PATHWAYS_ALPHA = "gw.pathways.alpha"
    GW_RT_PERFECTFORESIGHT = "gw.rt.perfectforesight"
    ISONEEXPRESS_FINALRT_HR_WEB = "isoneexpress.finalrt.hr.web"
    ERCOT_RTM15_APIZIP = "ercot.rtm15.apizip"
    GW_RTFROMDA_ALPHA = "gw.rtfromda.alpha"
    EPEXSPOT_WEB = "epexspot.web"
    ISONEEXPRESS_GRABREAL_FINALRT_HR_WEB = "isoneexpress.grabreal.finalrt.hr.web"
    GW_DA_PREDICTED_ROLLING4WKS_ALPHA = "gw.da.predicted.rolling4wks.alpha"
    GW_RTFROMDA_PERFECTFORESIGHT = "gw.rtfromda.perfectforesight"
    GW_PERFECTRTFOR2_THEN_DA = "gw.perfectrtfor2.then.da"
    GW_PERFECTRTFOR12_THEN_DA = "gw.perfectrtfor12.then.da"
    GAIA_ERCOT_RT_BETA = "gaia.ercot.rt.beta"
    ERCOT_DAM60_APIZIP = "ercot.dam60.apizip"
