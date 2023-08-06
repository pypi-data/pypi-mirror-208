import csv
import json
from typing import List

from gridworks.algo_utils import BasicAccount

from gwatn.types import TadeedSpecsHack_Maker


defaults_file = "input_data/ta_nft_data.csv"
rows: List[str] = []
with open(defaults_file) as csv_file:
    reader = csv.reader(csv_file)
    for row in reader:
        rows.append(row)


plant_names: List[str] = []
for i in range(1, len(rows)):
    plant = rows[i][0].strip()
    plant_names.append(plant)

dups = []
pnames = []
for p in plant_names:
    if p in pnames:
        dups.append(p)
    else:
        pnames.append(p)

if len(dups) > 0:
    raise Exception(f"Duplicate plant names: {dups}")

for i in range(1, len(rows)):
    plant = rows[i][0].strip()
    lat = int(rows[i][1])
    lon = int(rows[i][2])
    port: str = rows[i][3].strip()
    ta_alias = f"d1.isone.ver.keene.{plant}.ta"
    payload = TadeedSpecsHack_Maker(
        terminal_asset_alias=ta_alias, micro_lat=lat, micro_lon=lon, daemon_port=port
    ).tuple
    file_name = (
        f"input_data/eventstore/d1.isone.ver.keene.{plant}.ta-tadeed.specs.hack.json"
    )
    with open(file_name, "w") as f:
        f.write(json.dumps(payload.as_dict()))
