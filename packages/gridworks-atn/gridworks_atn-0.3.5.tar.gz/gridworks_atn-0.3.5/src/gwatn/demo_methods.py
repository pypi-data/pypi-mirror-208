import json
import logging
import subprocess
import sys
import time
from typing import List

import gridworks.api_utils as api_utils
import gridworks.dev_utils.algo_setup as algo_setup
from gridworks.algo_utils import BasicAccount
from gridworks.utils import RestfulResponse
from pydantic import SecretStr
from rich.pretty import pprint

import gwatn.config as config
from gwatn.dev_utils import DevDiscoverer
from gwatn.dev_utils import DevTaOwner
from gwatn.dev_utils import DevValidator
from gwatn.types import BaseGNodeGt_Maker
from gwatn.types import TadeedSpecsHack_Maker


logging.basicConfig(level="INFO")
LOGGER = logging.getLogger(__name__)


def certify_molly_metermaid() -> RestfulResponse:
    molly = DevValidator(config.ValidatorSettings())
    cert_idx = api_utils.get_validator_cert_idx(validator_addr=molly.acct.addr)
    if cert_idx is not None:
        raise Exception(
            f"There is already a Validator Certificate for Molly! Please ./sandbox reset and start the demo over."
        )
    return molly.post_tavalidatorcert_algo_create()


def create_ta_owner(plant: str) -> DevTaOwner:
    file = f"input_data/eventstore/d1.isone.ver.keene.{plant}.ta-tadeed.specs.hack.json"
    with open(file) as f:
        payload = TadeedSpecsHack_Maker.dict_to_tuple(json.load(f))

    settings = config.TaOwnerSettings()
    ta_owner_acct = BasicAccount()
    settings.sk = SecretStr(ta_owner_acct.sk)
    settings.initial_ta_alias = payload.TerminalAssetAlias
    settings.ta_daemon_api_port = payload.DaemonPort
    ta_owner = DevTaOwner(settings)
    return ta_owner


def create_ta_owners(plants: List[str]) -> List[DevTaOwner]:
    owners: List[DevTaOwner] = []
    for plant in plants:
        owners.append(create_ta_owner(plant))
    return owners


def start_ta_owners(ta_owners: List[DevTaOwner]) -> RestfulResponse:
    started_ta_owners: List[DevTaOwner] = []
    for owner in ta_owners:
        try:
            owner.start()
        except:
            for owner in started_ta_owners:
                owner.stop()
            return RestfulResponse(
                Note=f"Error starting {owner.settings.initial_ta_alias} owner.",
                HttpStatusCode=422,
            )
        started_ta_owners.append(owner)
    return RestfulResponse(Note="Successfully started all TaOwners and TaDaemons")


def create_terminal_asset(ta_owner: DevTaOwner) -> RestfulResponse:
    molly = DevValidator(config.ValidatorSettings())
    rr = ta_owner.request_ta_certification()
    if rr.HttpStatusCode > 200:
        note = (
            f"Stopping demo due to errors in requesting ta certification for "
            f"{ta_owner.settings.initial_ta_alias}" + rr.Note
        )
        return RestfulResponse(Note=note, HttpStatusCode=422)
    pprint(rr)
    terminal_asset = BaseGNodeGt_Maker.dict_to_tuple(rr.PayloadAsDict)
    ta_deed_idx = terminal_asset.OwnershipDeedId
    LOGGER.info(f"Made TaDeed {ta_deed_idx} for {terminal_asset.Alias}")

    rr = molly.certify_terminal_asset(
        ta_deed_idx=ta_deed_idx,
        ta_daemon_addr=ta_owner.ta_daemon_acct.addr,
        ta_owner_addr=ta_owner.acct.addr,
        micro_lat=ta_owner.settings.micro_lat,
        micro_lon=ta_owner.settings.micro_lon,
    )

    if rr.HttpStatusCode > 200:
        note = (
            "Stopping demo due to errors certifying terminal asset for "
            f"{ta_owner.settings.initial_ta_alias}" + rr.Note
        )
        return RestfulResponse(Note=note, HttpStatusCode=422)
    pprint(rr)
    return rr


def create_terminal_assets(ta_owners: List[DevTaOwner]) -> RestfulResponse:
    for ta_owner in ta_owners:
        if not isinstance(ta_owner, DevTaOwner):
            return RestfulResponse(
                Note=f"{ta_owner} is not a DevTaOwner!", HttpStatusCode=422
            )
    for ta_owner in ta_owners:
        rr = create_terminal_asset(ta_owner)
        if rr.HttpStatusCode > 200:
            for ta_owner in ta_owners:
                ta_owner.stop()
            return rr
    return RestfulResponse(Note="Success with create_terminal_assets")


def create_scadas(ta_owners: List[DevTaOwner]) -> RestfulResponse:
    for ta_owner in ta_owners:
        if not isinstance(ta_owner, DevTaOwner):
            return RestfulResponse(
                Note=f"{ta_owner} is not a DevTaOwner!", HttpStatusCode=422
            )
    for ta_owner in ta_owners:
        rr = ta_owner.create_scada_g_node()
        if rr.HttpStatusCode > 200:
            for ta_owner in ta_owners:
                ta_owner.stop()
            return rr
    return RestfulResponse(Note="Success with create_scadas")


def enter_slas(ta_owners: List[DevTaOwner]) -> RestfulResponse:
    for ta_owner in ta_owners:
        if not isinstance(ta_owner, DevTaOwner):
            return RestfulResponse(
                Note=f"{ta_owner} is not a DevTaOwner!", HttpStatusCode=422
            )
    for ta_owner in ta_owners:
        rr = ta_owner.enter_sla()
        if rr.HttpStatusCode > 200:
            for ta_owner in ta_owners:
                ta_owner.stop()
            return rr
    return RestfulResponse(Note="Success with entering ServiceLevelAgreements")


def create_new_ctn():
    ada = DevDiscoverer(settings=config.DiscovererSettings())
    rr = ada.post_discoverycert_algo_create()
    LOGGER.info("Ada received response to discoverycert algo")


demo_plant_names: List[str] = [
    "holly",
    "juniper",
    "violet",
    "lettuce",
    "mushroom",
    "nettle",
    "orange",
    "pine",
    "quinoi",
    "rose",
    "leek",
    "umbrella",
    "kale",
    "wasabi",
    "yarrow",
    "zinnia",
    "apple",
    "beet",
    "acacia",
    "buxus",
    "calathea",
    "chestnut",
    "columnea",
    "cuphea",
    "dracaena",
    "eucharis",
    "gardenia",
    "hedera",
    "ixora",
    "lemon",
    "mansoa",
    "murraya",
    "pepper",
    "pilea",
    "redwood",
    "stapelia",
    "acca",
    "begonia",
    "callisia",
    "citronella",
    "cordyline",
    "cyanotis",
    "drosera",
    "euphorbia",
    "gasteria",
    "orchid",
    "jacobinia",
    "lepanthes",
    "maple",
    "myrtle",
    "pandanus",
    "punica",
    "rhapis",
    "strelitzia",
    "acorus",
    "billbergia",
    "campanula",
    "cleyera",
    "corokia",
    "cycas",
    "duchesnea",
    "exacum",
    "gloriosa",
    "hibiscus",
    "jasmine",
    "lilium",
    "maranta",
    "neoregelia",
    "passiflora",
    "pineapple",
    "rhoeo",
    "thistle",
    "aechmea",
    "biophytum",
    "capsicum",
    "clivia",
    "costus",
    "cyclamen",
    "carrot",
    "fatshedera",
    "gongora",
    "hoffmannia",
    "jatropha",
    "redbud",
    "maxillaria",
    "nepenthes",
    "celery",
    "pisonia",
    "rivina",
    "thunia",
    "aeonium",
    "birch",
    "caryota",
    "coccoloba",
    "cottonwood",
    "cyperus",
    "elm",
    "fatsia",
    "guzmania",
    "howea",
    "kalanchoe",
    "lily",
    "medinilla",
    "nerine",
    "pellionia",
    "pleione",
    "rochea",
    "tolmiea",
    "agapetes",
    "blechnum",
    "cattleya",
    "coconut",
    "cotyledon",
    "datura",
    "encyclia",
    "ficus",
    "gynura",
    "hoya",
    "kohleria",
    "liriope",
    "miltonia",
    "nertera",
    "pentas",
    "plumbago",
    "ruellia",
    "tomato",
    "agave",
    "bouvardia",
    "ceropegia",
    "coffea",
    "crassula",
    "dionaea",
    "epidendrum",
    "fir",
    "haemaria",
    "hydrangea",
    "laelia",
    "livistona",
    "mimosa",
    "oak",
    "peperomia",
    "polyscias",
    "saffron",
    "radish",
    "aloe",
    "brunfelsia",
    "chenolle",
    "coleus",
    "crinum",
    "dipladenia",
    "episcia",
    "fittonia",
    "haworth",
    "impatiens",
    "lantana",
    "macodes",
    "molineria",
    "oleander",
    "petunia",
    "primrose",
    "sanchezia",
    "willow",
    "beech",
    "cactus",
    "cherimoya",
    "colmanara",
    "crossandra",
    "dischidia",
    "erica",
    "fuchsia",
    "haworthia",
    "iresine",
    "laurus",
    "mallow",
    "monstera",
    "oncidium",
    "phoenix",
    "primula",
    "spruce",
    "camellia",
]


def cert_creation(sim_size: int) -> List[DevTaOwner]:
    plant_names = demo_plant_names[0:sim_size]
    if sim_size == 0:
        raise Exception("No simulated TerminalAssets. Stopping")
    elif sim_size == 1:
        print(f"Running simulation for 1 TerminalAsset (holly.ta)")
    elif sim_size > 4:
        raise Exception("Please choose between 1 and 4 TerminalAssets")
    else:
        print(f"Running simulation for {sim_size} TerminalAssets")
    time.sleep(2)
    print("")

    print("")
    print("")
    print("Funding GNodeFactory")

    algo_setup.dev_fund_to_min(config.Public().gnf_admin_addr, 25)
    algo_setup.dev_fund_to_min(config.Public().gnf_graveyard_addr, 1)

    print("")
    print("")
    print(f"Funding {sim_size} Atn accts")
    print("")
    print("")

    atn_address_list = [
        "4JHRDNY4F6RCVGPALZULZWZNVP3OKT3DATEOLINCGILVPGHUOFY7KCHVIQ",
        "YL3MAWSIST2DWX5GOTZYVX74GNSAVMX52RKSEDT4KIO644JCCRFTFKM5UM",
        "CWOLXCXZKLYLORBQQCI4AUHA5CLOLUXRDZEJZI4S3F6WUNVIAF4MX5EW4U",
        "R3PKD54UOAOW6MTPO7ECZ6YX4COQWN5BJM4OZIHYWFVVGAITM53RGUF6LI",
    ]

    for i in range(sim_size):
        addr = atn_address_list[i]
        algo_setup.dev_fund_to_min(addr=addr, min_algos=25)

    addr = atn_address_list[0]
    print("")
    print("")
    print("Certifying MollyMetermaid as a TaValidator")
    print("")
    print("")
    time.sleep(2)

    # print("")
    # print("")
    # print("Starting up Molly Metermaid's Validator API")
    # print("")
    # print("")
    # time.sleep(2)
    # cmd = "docker compose -f docker-api.yml up -d"
    # subprocess.run(cmd.split())

    # print("Verify that it works by inspecting http://localhost:8001/docs")
    # print("")
    # print("")

    # time.sleep(2)
    # print("This also started up the API half of the MarketMaker.")
    # print("Verify that it is working:")

    # print("- http://localhost:7997/ shows market maker information")
    # print(
    #     "- http://localhost:7997/get-time/, which should be 0 unix time, but will show the time"
    # )
    # print(" of the simulation once that starts")

    rr = certify_molly_metermaid()

    pprint(rr)
    if rr.HttpStatusCode > 200:
        raise Exception("Stopping demo due to errors")

    print("")
    print("")
    print(f"Creating {sim_size} TaOwners")
    print("")
    print("")
    time.sleep(2)
    ta_owners = create_ta_owners(plant_names)
    print("")
    print("")
    print(f"Creating {sim_size} TaDaemons")
    print("")
    print("")
    time.sleep(2)
    start_ta_owners(ta_owners)

    print("")
    print("")
    print("TaDaemons are now running, each with their own RestAPI.")
    print("")
    print("")
    time.sleep(2)
    print("Any TaDeeds they own will show up at the following endpoints:")
    print("")
    print("")
    for owner in ta_owners:
        print(
            f"Inspect {owner}'s deeds at http://localhost:{owner.settings.ta_daemon_api_port}/owned-tadeeds/"
        )

    print("")
    print("")
    time.sleep(2)
    print("They do not yet own any TaDeeds.")
    print("")
    print("")
    time.sleep(2)
    input("HIT RETURN TO CONTINUE")

    print("")
    print("")
    print(f"Creating {sim_size} TerminalAssets")
    print("")
    print("")
    time.sleep(2)

    rr = create_terminal_assets(ta_owners)

    if rr.HttpStatusCode == 200:
        print("Success!")
        print("")
        print("")
        time.sleep(2)
        print(
            "TaDaemon Algorand addresses now hold TaDeeds on behalf of their TaOwners"
        )
        print("")
        print("")
        time.sleep(2)
        print("Inspect them at:")

        for owner in ta_owners:
            print(
                f"Inspect {owner}'s deeds at http://localhost:{owner.settings.ta_daemon_api_port}/owned-tadeeds/"
            )

    else:
        for ta_owner in ta_owners:
            ta_owner.stop()  # Does the same
        raise Exception(
            f"Something went wrong creating TerminalAssets: {rr.HttpStatusCode}, {rr.Note}"
        )

    print("")
    print("")
    print(
        "The AtomicTNodes do not yet own trading rights. Inspect trading right owners at:"
    )
    for owner in ta_owners:
        print(
            f"Inspect {owner}'s deeds at http://localhost:{owner.settings.ta_daemon_api_port}/trading-rights/"
        )

    print("")
    print("")
    time.sleep(2)
    input("HIT RETURN TO CONTINUE")
    print("")
    print("")
    print(
        "In fact the AtomicTNodes and SCADAS do not exist yet. Go to http://d1-1.electricity.works:15672/#/queues"
    )
    print("")
    print("")
    time.sleep(1)
    print("Username and password are the same:")
    print("")
    print("smqPublic")
    print("")
    print("")
    time.sleep(1)
    print("When they do, you will see queues representing AtomicTNodes and SCADAS ")
    # input("To start the atn actors (and time coordinator) in a docker instance, HIT RETURN")
    # )
    # print("")
    # print("")
    # print("It takes about 5 seconds for them to shop up. Look for them at")
    # print("http://d1-1.electricity.works:15672/#/queues")
    # print(
    #     "Once their queues exist they ready to enter their Service Level Agreements and get their trading rights"
    # )
    # input("HIT RETURN TO CONTINUE")
    rr = enter_slas(ta_owners)

    if rr.HttpStatusCode == 200:
        print("")
        print("")
        time.sleep(2)
        print(
            "Daemons have transferred TradingRights to their AtomicTNodes. Inspect at above pages"
        )
        print("")
        print("")
    else:
        cmd = "docker compose -f docker-actor.yml down"
        subprocess.run(cmd.split())
        raise Exception("Something went wrong entering Service Level Agreements")

    print("")
    print("")
    print(f"Getting SCADA Certs for {sim_size} Scada")
    print("")
    print("")
    time.sleep(2)

    rr = create_scadas(ta_owners)

    if rr.HttpStatusCode == 200:
        print("Success!")
        print("")
        print("")
        time.sleep(2)
        print("Scada accounts are funded, and Scada Certs are created")

    else:
        for ta_owner in ta_owners:
            ta_owner.stop()  # Does the same
        raise Exception(
            f"Something went wrong creating TerminalAssets: {rr.HttpStatusCode}, {rr.Note}"
        )
    return ta_owners
