import logging
import subprocess
from typing import Optional

import gridworks.algo_utils as algo_utils
import gridworks.dev_utils.algo_setup as algo_setup
import gridworks.errors as errors
import requests
from algosdk import encoding
from algosdk.future.transaction import *
from algosdk.v2client.algod import AlgodClient
from gridworks.algo_utils import BasicAccount
from gridworks.algo_utils import MultisigAccount
from gridworks.utils import RestfulResponse

import gwatn.config as config
from gwatn.dispatch_contract import DispatchContract

# Sent by homeowner
from gwatn.types import BaseGNodeGt_Maker
from gwatn.types import BasegnodeScadaCreate_Maker
from gwatn.types import InitialTadeedAlgoOptin_Maker
from gwatn.types import SlaEnter_Maker
from gwatn.types import TerminalassetCertifyHack_Maker


LOGGER = logging.getLogger(__name__)


class DevTaOwner:
    def __init__(
        self,
        settings: config.TaOwnerSettings,
    ):
        LOGGER.info(f"Initializing TaOwner for {settings.initial_ta_alias}")

        self.settings = settings
        self.scada_sk_by_ta_alias = {
            "d1.isone.ver.keene.holly.ta": "7RaOTVzqiL5NHarfkp7FpR1rjmn3T4Nibd+017Uhd9GpOVe2and91D46zJxO1wycU02TXxVu18cmslBEKgb8IA==",
            "d1.isone.ver.keene.juniper.ta": "K1tymo7Y9Lr2ACt67JGgUYAgeZA+Ufr9vICxn4643TI8Cxq6Mk/fdHwqOBByarqvGT80Q4GZTeyuQBWwwre54w==",
            "d1.isone.ver.keene.violet.ta": "sWThfGj1CeWD1MU1ZRkzQjBrP5F3G5Ij1XewTqp8FCr7bDmlfuY5G1GQju6rBNHVs5DKshtEaWyBgvXqV7aeNA==",
            "d1.isone.ver.keene.lettuce.ta": "GHY1eOFzSQsWM2BlhLGlNJc5JhAFN9yP0suUZ9usCnuisN9OiU/6TyHcuZczZDLFBi6LZCEzWActfaiMmfaKKw==",
        }

        self.scada_addr_by_ta_alias = {
            "d1.isone.ver.keene.holly.ta": "VE4VPNTKO565IPR2ZSOE5VYMTRJU3E27CVXNPRZGWJIEIKQG7QQKFVXDYE",
            "d1.isone.ver.keene.juniper.ta": "HQFRVORSJ7PXI7BKHAIHE2V2V4MT6NCDQGMU33FOIAK3BQVXXHRWJY6VWI",
            "d1.isone.ver.keene.violet.ta": "7NWDTJL64Y4RWUMQR3XKWBGR2WZZBSVSDNCGS3EBQL26UV5WTY2CUK6OJI",
            "d1.isone.ver.keene.lettuce.ta": "UKYN6TUJJ75E6IO4XGLTGZBSYUDC5C3EEEZVQBZNPWUIZGPWRIVQSOK6QA",
        }
        self.client: AlgodClient = AlgodClient(
            settings.algo_api_secrets.algod_token.get_secret_value(),
            settings.public.algod_address,
        )
        self.sp = self.client.suggested_params()
        self.acct: BasicAccount = BasicAccount(
            private_key=self.settings.sk.get_secret_value()
        )

        algos = (
            self.settings.public.ta_deed_consideration_algos
            + DispatchContract.min_balance
            + 11
        )
        algo_setup.dev_fund_to_min(self.acct.addr, algos)
        LOGGER.info(
            f"HollyHomeowner acct {self.acct.addr_short_hand} balance: ~{algo_utils.algos(self.acct.addr)} Algos"
        )

        self.validator_multi = MultisigAccount(
            version=1,
            threshold=2,
            addresses=[
                self.settings.public.gnf_admin_addr,
                self.settings.ta_validator_addr,
            ],
        )
        if self.settings.initial_ta_alias == "d1.isone.ver.keene.holly.ta":
            ta_daemon_sk = config.TaDaemonSettings().sk.get_secret_value()
            self.ta_daemon_acct = BasicAccount(ta_daemon_sk)
        else:
            self.ta_daemon_acct: BasicAccount = BasicAccount()
            self.settings.ta_daemon_addr = self.ta_daemon_acct.addr

        self.ta_daemon_api_root = (
            f"{self.settings.ta_daemon_api_fqdn}:{self.settings.ta_daemon_api_port}"
        )
        LOGGER.info(f"ta_owner_addr = {self.acct.addr}")
        LOGGER.info(f"ta_daemon_addr = {self.ta_daemon_acct.addr}")

    def start(self):
        LOGGER.info(
            f"Starting {self.short_alias}-daemon on port {self.settings.ta_daemon_api_port}"
        )
        self.pr: subprocess.Popen = self.start_ta_daemon()

    def stop(self):
        # self.pr.terminate()
        cmd = f"docker stop {self.short_alias}-daemon"
        subprocess.run(cmd.split())
        cmd = f"docker rm {self.short_alias}-daemon"
        subprocess.run(cmd.split())
        cmd = f"docker stop {self.short_alias}-scada"
        subprocess.run(cmd.split())
        cmd = f"docker rm {self.short_alias}-scada"
        subprocess.run(cmd.split())

    def start_scada_actor(self, scada_cert_idx: int) -> Optional[subprocess.Popen]:
        return None
        # ta_alias = self.settings.initial_ta_alias
        # scada_alias = ".".join(ta_alias.split(".")[:-1]) + '.scada'
        # scada_sk = self.scada_sk_by_ta_alias[ta_alias]
        # cmd = f"docker run  -e SCADA_G_NODE_ALIAS={scada_alias} -e SCADA_SK={scada_sk} --name {self.short_alias}-scada jessmillar/scada:latest"
        # pr = subprocess.Popen(
        #     cmd.split(),
        # )
        # return pr

    def start_ta_daemon(self) -> subprocess.Popen:
        LOGGER.info("Starting TaDaemon")
        port = self.settings.ta_daemon_api_port
        cmd = f"docker run  -e TAD_SK={self.ta_daemon_acct.sk} -e TAD_TA_OWNER_ADDR={self.acct.addr} -p {port}:8000 --name {self.short_alias}-daemon jessmillar/python-ta-daemon:chaos__2e38992__20221231"
        pr = subprocess.Popen(
            cmd.split(),
        )

        daemon_api_root = (
            f"{self.settings.ta_daemon_api_fqdn}:{self.settings.ta_daemon_api_port}"
        )
        api_endpoint = f"{daemon_api_root}/"
        daemon_up: bool = False
        while not daemon_up:
            try:
                daemon_up = True
                requests.get(url=api_endpoint)
            except:
                daemon_up = False
        return pr

    def __repr__(self) -> str:
        return self.short_alias

    ##########################
    # Messages Sent
    ##########################

    def create_scada_g_node(self) -> RestfulResponse:
        txn = PaymentTxn(
            sender=self.acct.addr,
            sp=self.sp,
            receiver=self.scada_addr_by_ta_alias[self.settings.initial_ta_alias],
            amt=DispatchContract.min_balance + 10_000_000,
        )
        signed_txn = txn.sign(self.acct.sk)
        ta_alias = self.settings.initial_ta_alias
        try:
            self.client.send_transaction(signed_txn)
        except Exception as e:
            note = f"Algorand Failure sending transaction: {e}"
            raise errors.AlgoError(note)
        payload = BasegnodeScadaCreate_Maker(
            ta_alias=ta_alias,
            scada_addr=self.scada_addr_by_ta_alias[ta_alias],
            ta_daemon_addr=self.settings.ta_daemon_addr,
            g_node_registry_addr=self.settings.public.gnr_addr,
            signed_proof=encoding.msgpack_encode(signed_txn),
        ).tuple
        api_endpoint = f"{self.settings.public.gnf_api_root}/basegnode-scada-create/"
        r = requests.post(url=api_endpoint, json=payload.as_dict())
        if r.status_code > 200:
            if r.status_code == 422:
                note = f"Error entering SLA: " + r.json()["detail"]
            else:
                note = r.reason
            rr = RestfulResponse(Note=note, HttpStatusCode=422)
            return rr
        rr = RestfulResponse(**r.json())
        if rr.PayloadTypeName != "base.g.node.gt":
            return RestfulResponse(
                Note=f"expected base.g.node.gt as PayloadTypeName, got {rr.PayloadTypeName}",
                HttpStatusCode=422,
            )
        scada_gt = BaseGNodeGt_Maker.dict_to_tuple(rr.PayloadAsDict)
        if scada_gt.ScadaCertId is None:
            return RestfulResponse(
                Note=f"expected ScadaCertId in returned BaseGNodeGt, got None",
                HttpStatusCode=422,
            )
        LOGGER.info(
            f"Successful request for Scada. ScadaCertId is {scada_gt.ScadaCertId}"
        )
        self.start_scada_actor(scada_cert_idx=scada_gt.ScadaCertId)
        # LOGGER.info(f"Started Scada actor for {scada_gt.Alias}")

        return rr

    def enter_sla(self) -> RestfulResponse:
        ta_alias = self.settings.initial_ta_alias
        payload = SlaEnter_Maker(terminal_asset_alias=ta_alias).tuple
        api_endpoint = f"{self.ta_daemon_api_root}/sla-enter/"
        r = requests.post(url=api_endpoint, json=payload.as_dict())
        if r.status_code > 200:
            if r.status_code == 422:
                note = f"Error entering SLA: " + r.json()["detail"]
            else:
                note = r.reason
            rr = RestfulResponse(Note=note, HttpStatusCode=422)
            return rr
        return RestfulResponse(**r.json())

    def request_ta_certification(self) -> RestfulResponse:
        ta_alias = self.settings.initial_ta_alias
        payload = TerminalassetCertifyHack_Maker(
            terminal_asset_alias=ta_alias,
            ta_daemon_api_fqdn=self.settings.ta_daemon_api_fqdn,
            ta_daemon_api_port=self.settings.ta_daemon_api_port,
            ta_daemon_addr=self.settings.ta_daemon_addr,
        ).tuple

        LOGGER.info(f"Requesting certification for {ta_alias}")
        api_endpoint = (
            f"{self.settings.ta_validator_api_root}/terminalasset-certification/"
        )
        try:
            r = requests.post(url=api_endpoint, json=payload.as_dict())
        except:
            return RestfulResponse(
                Note=f"Validator address {api_endpoint} does not exist!",
                HttpStatusCode=422,
            )
        if r.status_code > 200:
            if r.status_code == 422:
                note = (
                    f"Error posting terminalasset-certification to validator: "
                    + r.json()["detail"]
                )
            else:
                note = r.reason
            rr = RestfulResponse(Note=note, HttpStatusCode=422)
            return rr
        rr1 = RestfulResponse(**r.json())
        rr2 = self.post_initial_tadeed_algo_optin()
        if rr2.HttpStatusCode > 200:
            return rr2
        return rr1

    def post_initial_tadeed_algo_optin(self) -> RestfulResponse:
        """
         - Sends 50 algos to TaDaemon acct
         - Sends InitialTadeedAlgoOptin to TaDaemon, with signed
         funding txn for proof of identity.

        Returns:
            RestfulResponse
        """
        LOGGER.info("Funding TaDaemon")
        required_algos = config.Public().ta_deed_consideration_algos
        txn = PaymentTxn(
            sender=self.acct.addr,
            receiver=self.settings.ta_daemon_addr,
            amt=required_algos * 10**6,
            sp=self.sp,
        )
        signed_txn = txn.sign(self.acct.sk)
        try:
            self.client.send_transaction(signed_txn)
        except Exception as e:
            note = f"Algorand Failure sending transaction: {e}"
            raise errors.AlgoError(note)
        algo_utils.wait_for_transaction(self.client, signed_txn.get_txid())
        payload = InitialTadeedAlgoOptin_Maker(
            terminal_asset_alias=self.settings.initial_ta_alias,
            ta_owner_addr=self.acct.addr,
            validator_addr=self.settings.ta_validator_addr,
            signed_initial_daemon_funding_txn=encoding.msgpack_encode(signed_txn),
        ).tuple
        api_endpoint = f"{self.ta_daemon_api_root}/initial-tadeed-algo-optin/"
        r = requests.post(url=api_endpoint, json=payload.as_dict())
        if r.status_code > 200:
            if r.status_code == 422:
                note = "Issue with InitialTadeedAlgoOptin" + r.json()["detail"]
            else:
                note = r.reason
            rr = RestfulResponse(Note=note, HttpStatusCode=422)
            return rr
        return RestfulResponse(**r.json())

    ##########################
    # dev methods
    ########################

    @property
    def short_alias(self) -> str:
        alias = self.settings.initial_ta_alias
        words = alias.split(".")
        return ".".join(words[-2:-1])
