import time

import gridworks.conversion_factors as cf
import pendulum
import xlsxwriter
from satn.strategies.heatpumpwithbooststore.flo import HeatPumpWithBoostStore__Flo
from satn.strategies.heatpumpwithbooststore.node import (
    Node_SpaceHeat__WaterStore as Node,
)

import gwatn.brick_storage_heater.strategy_utils as strategy_utils
from gwatn.brick_storage_heater.edge import Edge__BrickStorageHeater as Edge
from gwatn.enums import RecognizedCurrencyUnit
from gwatn.types import AtnParamsBrickstorageheater as AtnParams


OUTPUT_FOLDER = "output_data"

ON_PEAK_DIST_PRICE_PER_MWH_CUTOFF = 100
SHOULDER_PEAK_DIST_PRICE_PER_MWH_CUTOFF = 50


def export_xlsx(alias: str, flo: HeatPumpWithBoostStore__Flo, atn_params: AtnParams):
    local_start = pendulum.timezone(flo.timezone_string).convert(flo.flo_start_utc)
    date_str = local_start.strftime("%Y%m%d")
    hour_str = local_start.strftime("%H")
    file = (
        OUTPUT_FOLDER + f"/result_{alias}_{date_str}_{hour_str}_{int(time.time())}.xlsx"
    )
    # flo.graph_strategy_alias,

    file = file.lower()
    print(file)

    workbook = xlsxwriter.Workbook(file)
    starting_store_idx = flo.starting_store_idx

    # Add to gsr for more blank rows
    gsr = 30
    w = export_best_path_info(
        alias=alias, flo=flo, workbook=workbook, starting_store_idx=starting_store_idx
    )

    export_flo_graph(
        flo=flo,
        workbook=workbook,
        worksheet=w,
        starting_store_idx=starting_store_idx,
        graph_start_row=gsr,
    )

    export_params_xlsx(flo=flo, atn_params=atn_params, workbook=workbook)
    workbook.close()


def export_best_path_info(
    alias: str,
    flo: HeatPumpWithBoostStore__Flo,
    workbook: xlsxwriter.workbook.Workbook,
    starting_store_idx: int,
):
    w = workbook.add_worksheet(
        f"start {100 * starting_store_idx / flo.params.StorageSteps}%"
    )
    w.freeze_panes(0, 2)
    title_format = workbook.add_format({"bold": True})
    title_format.set_font_size(14)
    bold_format = workbook.add_format({"bold": True})
    gray_filler_format = workbook.add_format({"bg_color": "#edf0f2"})
    header_format = workbook.add_format({"bold": True, "text_wrap": True})
    mwh_format = workbook.add_format({"bold": True, "num_format": '0.00" MWh"'})
    if flo.params.CurrencyUnit == RecognizedCurrencyUnit.USD:
        currency_format = workbook.add_format({"num_format": "$#,##0.00"})
        currency_bold_format = workbook.add_format(
            {"bold": True, "num_format": "$#,##0.00"}
        )
    elif flo.params.CurrencyUnit == RecognizedCurrencyUnit.GBP:
        currency_format = workbook.add_format(
            {"num_format": "_-[$£-en-GB]* #,##0.00_-"}
        )
        currency_bold_format = workbook.add_format(
            {"bold": True, "num_format": "_-[$£-en-GB]* #,##0.00_-"}
        )

    w.set_column("A:A", 26)
    w.set_column("B:B", 15)
    OPT_PATH_STATE_VAR_ROW = 14

    swt_list = flo_utils.get_source_water_temp_f_list(flo.params)
    w.write(0, 0, f"GNode Alias: {alias}", title_format)
    w.write(1, 0, flo.graph_strategy_alias)
    w.write(2, 0, f"FLO start {flo.params.TimezoneString} ", header_format)
    local_start = pendulum.timezone(flo.timezone_string).convert(flo.flo_start_utc)
    w.write(2, 1, local_start.strftime("%Y/%m/%d %H:%M"))

    w.write(3, 0, "Total hours", header_format)
    w.write(3, 1, sum(flo.slice_duration_hrs), bold_format)

    w.write(4, 0, "Rt Energy Price ($/MWh)", header_format)
    w.write(
        4,
        1,
        sum(flo.RealtimeElectricityPrice) / len(flo.RealtimeElectricityPrice),
        currency_bold_format,
    )
    # w.write(5, 0, "Flat rate for hp ($/MWh)", header_format)
    # if flo.params.IsRegulating:
    #     w.write(5, 0, "Regulation Price ($/MWh)", header_format)
    #     w.write(
    #         5, 1, sum(flo.reg_price_per_mwh) / len(flo.reg_price_per_mwh), currency_bold_format
    #     )

    w.write(6, 0, "Dist Price ($/MWh)", header_format)
    w.write(
        6,
        1,
        sum(flo.DistributionPrice) / len(flo.DistributionPrice),
        currency_bold_format,
    )
    w.write(7, 0, "Outside Temp F", header_format)
    w.write(
        7,
        1,
        round(sum(flo.params.OutsideTempF) / len(flo.params.OutsideTempF), 2),
        bold_format,
    )
    w.write(8, 0, "COP", header_format)
    avg_cop = sum(flo.cop.values()) / len(flo.cop)
    w.write(8, 1, round(avg_cop, 2), bold_format)
    w.write(9, 0, "House Power Required AvgKw", header_format)
    w.write(
        9,
        1,
        round(sum(flo.params.PowerRequiredByHouseFromSystemAvgKwList), 2),
        bold_format,
    )
    w.write(10, 0, "Required Source Water Temp F", header_format)
    avg_swt = round((sum(swt_list) / len(swt_list)), 0)
    w.write(10, 1, avg_swt, bold_format)
    w.write(11, 0, "Max HeatPump kWh thermal", header_format)
    avg_max_thermal_hp_kwh = round(
        (sum(flo.max_thermal_hp_kwh.values()) / len(flo.max_thermal_hp_kwh)), 2
    )
    w.write(11, 1, avg_max_thermal_hp_kwh, bold_format)

    w.write(12, 0, "Outputs", header_format)

    for jj in range(flo.time_slices):
        hours_since_start = sum(flo.slice_duration_hrs[0:jj])
        local_time = local_start.add(hours=hours_since_start)
        w.write(2, jj + 2, local_time.strftime("%m/%d"))
        w.write(3, jj + 2, local_time.strftime("%H:%M"))
        w.write(4, jj + 2, flo.RealtimeElectricityPrice[jj], currency_format)
        if flo.params.IsRegulating:
            w.write(5, jj + 2, flo.reg_price_per_mwh[jj], currency_format)
        else:
            w.write(5, jj + 2, "", gray_filler_format)
        dp = flo.DistributionPrice[jj]
        LIGHT_GREEN_HEX = "#bbe3a6"
        LIGHT_RED_HEX = "#ff6363"
        if dp > ON_PEAK_DIST_PRICE_PER_MWH_CUTOFF:
            if flo.params.CurrencyUnit == RecognizedCurrencyUnit.USD:
                dist_format = workbook.add_format(
                    {"bg_color": LIGHT_RED_HEX, "num_format": "$#,##0.00"}
                )
            elif flo.params.CurrencyUnit == RecognizedCurrencyUnit.GBP:
                dist_format = workbook.add_format(
                    {
                        "bg_color": LIGHT_RED_HEX,
                        "num_format": "_-[$£-en-GB]* #,##0.00_-",
                    }
                )
        elif dp > SHOULDER_PEAK_DIST_PRICE_PER_MWH_CUTOFF:
            if flo.params.CurrencyUnit == RecognizedCurrencyUnit.USD:
                dist_format = workbook.add_format(
                    {"bg_color": "yellow", "num_format": "$#,##0.00"}
                )
            elif flo.params.CurrencyUnit == RecognizedCurrencyUnit.GBP:
                dist_format = workbook.add_format(
                    {"bg_color": "yellow", "num_format": "_-[$£-en-GB]* #,##0.00_-"}
                )
        else:
            if flo.params.CurrencyUnit == RecognizedCurrencyUnit.USD:
                dist_format = workbook.add_format(
                    {"bg_color": LIGHT_GREEN_HEX, "num_format": "$#,##0.00"}
                )
            elif flo.params.CurrencyUnit == RecognizedCurrencyUnit.GBP:
                dist_format = workbook.add_format(
                    {
                        "bg_color": LIGHT_GREEN_HEX,
                        "num_format": "_-[$£-en-GB]* #,##0.00_-",
                    }
                )
        w.write(6, jj + 2, flo.DistributionPrice[jj], dist_format)
        w.write(7, jj + 2, flo.params.OutsideTempF[jj])
        w.write(8, jj + 2, flo.cop[jj])
        w.write(
            9, jj + 2, round(flo.params.PowerRequiredByHouseFromSystemAvgKwList[jj], 2)
        )
        w.write(10, jj + 2, round(swt_list[jj], 0))
        w.write(11, jj + 2, round(flo.max_thermal_hp_kwh[jj], 2))

        w.write(12, jj + 2, "", gray_filler_format)

    node: Node = flo.node[0][starting_store_idx]
    w.write(OPT_PATH_STATE_VAR_ROW, 0, "Store Temp (F)", header_format)
    w.write(OPT_PATH_STATE_VAR_ROW + 1, 0, "HeatPump kWh thermal", header_format)
    w.write(OPT_PATH_STATE_VAR_ROW + 2, 0, "HeatPump kWh electric", header_format)
    w.write(OPT_PATH_STATE_VAR_ROW + 3, 0, "Boost kWh electric", header_format)
    w.write(OPT_PATH_STATE_VAR_ROW + 4, 0, "Energy cost (¢)", header_format)
    w.write(OPT_PATH_STATE_VAR_ROW + 5, 0, "Hours Since Start", header_format)

    store_temp_f = []
    opt_heatpump_electricity_used_kwh = []
    opt_boost_electricity_used_kwh = []
    opt_energy_cost_dollars = []

    best_idx = starting_store_idx
    dist_cost = []
    min_dist_price_per_mwh = min(flo.DistributionPrice)

    for jj in range(flo.time_slices):
        edge: Edge = flo.best_edge[node]
        store_temp_f.append(node.store_avg_water_temp_f)
        hp_kwh = edge.hp_electricity_avg_kw
        boost_kwh = edge.boost_electricity_used_avg_kw
        opt_heatpump_electricity_used_kwh.append(hp_kwh)
        opt_boost_electricity_used_kwh.append(boost_kwh)
        opt_energy_cost_dollars.append(edge.cost)
        hours_since_start = sum(flo.slice_duration_hrs[0:jj])

        w.write(OPT_PATH_STATE_VAR_ROW, jj + 2, round(node.store_avg_water_temp_f, 2))
        w.write(
            OPT_PATH_STATE_VAR_ROW + 1,
            jj + 2,
            round(edge.hp_thermal_energy_generated_avg_kw, 3),
        )
        w.write(
            OPT_PATH_STATE_VAR_ROW + 2, jj + 2, round(edge.hp_electricity_avg_kw, 3)
        )
        w.write(
            OPT_PATH_STATE_VAR_ROW + 3,
            jj + 2,
            round(edge.boost_electricity_used_avg_kw, 3),
        )
        w.write(OPT_PATH_STATE_VAR_ROW + 4, jj + 2, round(edge.cost * 100, 2))
        w.write(OPT_PATH_STATE_VAR_ROW + 5, jj + 2, round(hours_since_start, 1))
        node = flo.node[jj + 1][edge.end_idx]

    w.write(
        OPT_PATH_STATE_VAR_ROW,
        1,
        round(sum(store_temp_f) / len(store_temp_f), 0),
        bold_format,
    )
    w.write(
        OPT_PATH_STATE_VAR_ROW + 2,
        1,
        sum(opt_heatpump_electricity_used_kwh) / 1000,
        mwh_format,
    )
    w.write(
        OPT_PATH_STATE_VAR_ROW + 3,
        1,
        sum(opt_boost_electricity_used_kwh) / 1000,
        mwh_format,
    )
    w.write(
        OPT_PATH_STATE_VAR_ROW + 4,
        1,
        sum(opt_energy_cost_dollars),
        currency_bold_format,
    )

    w.write("H1", "Electricity cost of this path")
    total_cost = sum(opt_energy_cost_dollars)
    w.write("G1", total_cost, currency_bold_format)
    w.write("H2", "Total electricity MWh")
    total_electricity_mwh = (
        sum(opt_boost_electricity_used_kwh) + sum(opt_heatpump_electricity_used_kwh)
    ) / 1000
    w.write("G2", total_electricity_mwh, mwh_format)

    total_btu = sum(flo.params.PowerRequiredByHouseFromSystemAvgKwList) * cf.BTU_PER_KWH
    gallons_oil = total_btu / cf.BTU_PER_GALLON_OF_OIL / 0.85
    # assumes 85% efficient oil boiler

    w.write("L1", "Gallons of Oil")
    w.write("K1", round(gallons_oil), bold_format)

    w.write("L2", "Equivalent Price of Oil")
    w.write("K2", total_cost / gallons_oil, currency_bold_format)
    # w.write("H3", "Flat rate comparison")

    return w


def export_flo_graph(
    flo: HeatPumpWithBoostStore__Flo,
    workbook: xlsxwriter.workbook.Workbook,
    worksheet: xlsxwriter.workbook.Worksheet,
    starting_store_idx: int,
    graph_start_row: int,
):
    # worksheet.freeze_panes(graph_start_row - 1, 2)
    header_format = workbook.add_format({"bold": True, "text_wrap": True})
    percent_format = workbook.add_format({"num_format": '00.0"%"'})
    best_path_format = workbook.add_format({"bold": True, "bg_color": "#CDEBA6"})
    best_idx = starting_store_idx

    worksheet.write(graph_start_row - 1, 0, "Percent full", header_format)

    for mm in range(flo.params.StorageSteps + 1):
        kk = flo.params.StorageSteps - mm
        percent = round(100 * kk / flo.params.StorageSteps, 1)
        worksheet.write(graph_start_row + mm, 0, percent, percent_format)
    for jj in range(flo.time_slices):
        best_node = flo.node[jj][best_idx]
        for mm in range(flo.params.StorageSteps + 1):
            kk = flo.params.StorageSteps - mm
            node = flo.node[jj][kk]
            if kk == best_idx:
                try:
                    worksheet.write(
                        graph_start_row + mm,
                        jj + 2,
                        -round(node.path_benefit, 4),
                        best_path_format,
                    )
                except:
                    print(f"failed for best {jj},{kk}")
            else:
                try:
                    worksheet.write(
                        graph_start_row + mm, jj + 2, round(node.path_cost, 4)
                    )
                except:
                    print(f"failed for {jj},{kk}")
        best_idx = flo.best_edge[best_node].end_idx


def export_params_xlsx(
    flo: HeatPumpWithBoostStore__Flo,
    atn_params: AtnParams,
    workbook: xlsxwriter.workbook.Workbook,
):
    bold = workbook.add_format({"bold": True})
    w = workbook.add_worksheet("Params")
    derived_format_bold = workbook.add_format({"bold": True, "font_color": "green"})
    derived_format = workbook.add_format({"font_color": "green"})
    swt_list = flo_utils.get_source_water_temp_f_list(flo.params)
    w.set_column("A:A", 31)
    w.set_column("D:D", 31)
    w.set_column("G:G", 31)
    w.write("A1", "Key Parameters", bold)

    t = flo.params.OutsideTempF
    w.write("A4", "This Run ColdestTempF ", derived_format_bold)
    w.write("B4", min(t), derived_format)

    w.write("A5", "HouseWorstCaseTempF ", bold)
    w.write("B5", atn_params.HouseWorstCaseTempF)

    w.write("A7", "SystemMaxHeatOutputKwAvg", bold)
    w.write("B7", round(flo.params.SystemMaxHeatOutputKwAvg, 2))

    p = flo.params.PowerRequiredByHouseFromSystemAvgKwList
    w.write("A8", "This Run MaxHeatOutputKwAvg", derived_format_bold)
    w.write("B8", round(max(p), 2), derived_format)

    house_wc_kw = flo_utils.get_house_worst_case_heat_output_avg_kw(flo.params)
    w.write("A9", "HouseWorstCaseHeatOuputAvgKw", derived_format_bold)
    w.write("B9", round(house_wc_kw, 1), derived_format)

    w.write("A10", "HouseWorstCaseHeatOuput BTU/hr", derived_format_bold)
    w.write("B10", round(house_wc_kw * cf.BTU_PER_KWH), derived_format)

    w.write("A12", "EmitterMaxSafeSwtF", bold)
    w.write("B12", flo.params.EmitterMaxSafeSwtF)

    w.write("A13", "This Run SystemMaxHeatOutputSwtF", bold)
    w.write("B13", round(max(swt_list)))

    w.write("A14", "SystemMaxHeatOutputSWTF ", bold)
    w.write("B14", flo.params.SystemMaxHeatOutputSwtF)

    w.write("A15", "HeatPumpMaxWaterTempF ", bold)
    w.write("B15", flo.params.MaxHeatpumpSourceWaterTempF)

    w.write("A16", "RatedHeatpumpElectricityKw", bold)
    w.write("B16", flo.params.RatedHeatpumpElectricityKw)

    w.write("A17", "StoreMaxPowerKw", bold)
    w.write("B17", flo.params.StoreMaxPowerKw)

    if flo.params.EmitterPumpFeedbackModel == EmitterPumpFeedbackModel.ConstantDeltaT:
        w.write("A19", "SystemMaxHeatOutputDeltaTempF", bold)
        w.write("B19", flo.params.SystemMaxHeatOutputDeltaTempF)

        w.write("A20", "SystemMaxHeatOutputGpm", derived_format_bold)
        w.write("B20", round(flo.params.SystemMaxHeatOutputGpm, 2), derived_format)
    else:
        w.write("A19", "SystemMaxHeatOutputDeltaTempF", bold)
        w.write("B19", flo.params.SystemMaxHeatOutputDeltaTempF)

        w.write("A20", "SystemMaxHeatOutputGpm", derived_format_bold)
        w.write("B20", round(flo.params.SystemMaxHeatOutputGpm, 2), derived_format)

    w.write("A21", "Cop1TempF", bold)
    w.write("B21", flo.params.Cop1TempF)

    w.write("A22", "Cop4TempF", bold)
    w.write("B22", flo.params.Cop4TempF)

    w.write("A23", "StorePassiveLossRatio", bold)
    w.write("B23", flo.params.StorePassiveLossRatio)

    w.write("A25", "StorageSteps", bold)
    w.write("B25", flo.params.StorageSteps)

    #############

    annual_kwh = atn_params.AnnualHvacKwhTh
    annual_btu = round(cf.BTU_PER_KWH * annual_kwh)
    w.write("D3", "Annual HVAC kWhTh", bold)
    w.write("E3", annual_kwh)

    w.write("D4", "Annual HVAC MBTU", derived_format_bold)
    w.write("E4", round(annual_btu / 10**6), derived_format)

    w.write("D6", "StoreSizeGallons", bold)
    w.write("E6", flo.params.StoreSizeGallons)

    w.write("D7", "MaxStoreTempF", bold)
    w.write("E7", flo.params.MaxStoreTempF)

    w.write("D8", "ZeroPotentialEnergyWaterTempF", bold)
    w.write("E8", flo.params.ZeroPotentialEnergyWaterTempF)

    w.write("D9", "TotalStorageKwh", derived_format_bold)
    w.write("E9", round(flo.max_energy_kwh_th, 1), derived_format)

    w.write("D10", "TotalStorage BTU", derived_format_bold)
    w.write("E10", round(cf.BTU_PER_KWH * flo.max_energy_kwh_th), derived_format)

    w.write("D12", "EmitterPumpFeedbackModel", bold)
    w.write("E12", flo.params.EmitterPumpFeedbackModel.value)

    w.write("D13", "MixingValveFeedbackModel", bold)
    w.write("E13", flo.params.MixingValveFeedbackModel.value)

    w.write("D14", "IsRegulating", bold)
    w.write("E14", flo.params.IsRegulating)

    w.write("D19", "RoomTempF", bold)
    w.write("E19", flo.params.RoomTempF)

    w.write("D20", "AmbientPowerInKw", bold)
    w.write("E20", flo.params.AmbientPowerInKw)

    ###############

    w.write("G3", "HeatpumpTariff", bold)
    w.write("H3", flo.params.HeatpumpTariff.value)

    w.write("G4", "HeatpumpEnergySupplyType", bold)
    w.write("H4", flo.params.HeatpumpEnergySupplyType.value)

    w.write("G5", "BoostTariff", bold)
    w.write("H5", flo.params.BoostTariff.value)

    w.write("G6", "BoostEnergySupplyType", bold)
    w.write("H6", flo.params.BoostEnergySupplyType.value)

    w.write("G7", "StandardOfferPriceDollarsPerMwh", bold)
    w.write("H7", flo.params.StandardOfferPriceDollarsPerMwh)

    w.write("G8", "DistributionTariffDollarsPerMwh", bold)
    w.write("H8", flo.params.DistributionTariffDollarsPerMwh)

    w.write("A29", "WeatherUid", bold)
    w.write("B29", flo.params.WeatherUid)
    w.write("A31", "RtElecPriceUid", bold)
    w.write("B31", flo.params.RtElecPriceUid)

    w.write("A33", "DistPriceUid", bold)
    w.write("B33", flo.params.DistPriceUid)

    if flo.params.IsRegulating:
        w.write("A34", "LocalRegulationFile", bold)
        w.write("B34", regp_sync_100_handler.csv_file_by_uid(flo.params.RegPriceUid))
        w.write("A35", "RegPriceUid", bold)
        w.write("B35", flo.params.RegPriceUid)
