import csv
import json
import uuid

import pendulum

from gwatn.types import AtnParamsBrickstorageheater as AtnParams
from gwatn.types import AtnParamsBrickstorageheater_Maker as AtnParams_Maker
from gwatn.types import AtnParamsReport_Maker
from gwatn.types.csv_distp_sync import CsvDistpSync_Maker
from gwatn.types.csv_eprt_sync import CsvEprtSync_Maker
from gwatn.types.csv_weather_forecast_sync import CsvWeatherForecastSync_Maker


eprt_csv = "input_data/elec_price_data.csv"
ep = CsvEprtSync_Maker(elec_price_file=eprt_csv).tuple

distp_csv = "input_data/dist_price_data.csv"
dp = CsvDistpSync_Maker(dist_price_file=distp_csv).tuple

temp_csv = "input_data/temperature_data.csv"
temp = CsvWeatherForecastSync_Maker(weather_csv=temp_csv).tuple

params_file = "src/gwatn/brick_storage_heater/dev_atn_params_data.csv"
params = []
with open(params_file) as csv_file:
    reader = csv.reader(csv_file)
    for row in reader:
        params.append(row)
start = pendulum.datetime(year=2020, month=1, day=1, hour=4)

for j in range(1, 19):
    alias = params[1][j]
    atn_params = AtnParams(
        GNodeAlias=alias,
        MaxBrickTempC=params[3][j],
        RatedMaxPowerKw=params[4][j],
        C=params[5][j],
        ROff=params[6][j],
        ROn=params[7][j],
        RoomTempF=params[8][j],
        AnnualHvacKwhTh=params[9][j],
        BetaOt=params[10][j],
    )

    try:
        report = AtnParamsReport_Maker(
            g_node_alias=alias,
            g_node_instance_id=str(uuid.uuid4()),
            atn_params_type_name=AtnParams_Maker.type_name,
            time_unix_s=start.int_timestamp,
            params=atn_params,
            irl_time_unix_s=None,
        ).tuple
    except:
        print(f"Problem with {alias}")

    file_name = f"input_data/eventstore/{alias}-{AtnParamsReport_Maker.type_name}-{start.int_timestamp * 1000}.json"
    json_object = json.dumps(report.as_dict())

    # Writing to sample.json
    with open(file_name, "w") as outfile:
        outfile.write(json_object)
