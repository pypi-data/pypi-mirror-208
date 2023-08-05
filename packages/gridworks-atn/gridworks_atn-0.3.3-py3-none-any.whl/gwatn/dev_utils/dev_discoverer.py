import logging

import gridworks.algo_utils as algo_utils
import gridworks.api_utils as api_utils
import requests
from algosdk.v2client.algod import AlgodClient
from gridworks.algo_utils import BasicAccount
from gridworks.utils import RestfulResponse

import gwatn.config as config
from gwatn.enums import CoreGNodeRole
from gwatn.types import DiscoverycertAlgoCreate_Maker


LOGGER = logging.getLogger(__name__)


class DevDiscoverer:
    def __init__(self, settings: config.DiscovererSettings):
        self.settings = settings
        self.client: AlgodClient = AlgodClient(
            settings.algo_api_secrets.algod_token.get_secret_value(),
            settings.public.algod_address,
        )
        self.acct: BasicAccount = algo_utils.BasicAccount(
            private_key=self.settings.sk.get_secret_value()
        )
        self.multi: algo_utils.MultisigAccount = (
            api_utils.get_discoverer_account_with_admin(self.acct.addr)
        )
        # self.seed_fund_own_account()
        LOGGER.info("DevDiscoverer Initialized")

    def post_discoverycert_algo_create(self) -> RestfulResponse:
        payload = DiscoverycertAlgoCreate_Maker(
            g_node_alias=config.DiscovererSettings().discovered_ctn_alias,
            old_child_alias_list=config.DiscovererSettings().original_child_alias_list,
            discoverer_addr=self.acct.addr,
            supporting_material_hash="supporting material",
            core_g_node_role=CoreGNodeRole.ConductorTopologyNode,
            micro_lon=config.DiscovererSettings().micro_lon,
            micro_lat=config.DiscovererSettings().micro_lat,
        ).tuple
        api_endpoint = f"{config.GnfPublic().gnf_api_root}/discoverycert-algo-create/"
        r = requests.post(url=api_endpoint, json=payload.as_dict())
