import logging
from typing import Optional

import dotenv
import gridworks.algo_utils as algo_utils
import gridworks.api_utils as api_utils
import gridworks.dev_utils.algo_setup as algo_setup
import requests
from algosdk import encoding
from algosdk.future import transaction
from algosdk.v2client.algod import AlgodClient
from gridworks.algo_utils import BasicAccount
from gridworks.algo_utils import MultisigAccount
from gridworks.utils import RestfulResponse
from rich.pretty import pprint

import gwatn.config as config
from gwatn.types import InitialTadeedAlgoCreate_Maker
from gwatn.types import InitialTadeedAlgoTransfer_Maker
from gwatn.types import TavalidatorcertAlgoCreate
from gwatn.types import TavalidatorcertAlgoCreate_Maker
from gwatn.types import TavalidatorcertAlgoTransfer
from gwatn.types import TavalidatorcertAlgoTransfer_Maker
from gwatn.types import TerminalassetCertifyHack


LOGGER = logging.getLogger(__name__)


class DevValidator:
    def __init__(
        self,
        settings: config.ValidatorSettings = config.ValidatorSettings(
            _env_file=dotenv.find_dotenv()
        ),
    ):
        self.settings = settings
        self.acct: BasicAccount = BasicAccount(
            private_key=self.settings.sk.get_secret_value()
        )
        self.client: AlgodClient = AlgodClient(
            settings.algo_api_secrets.algod_token.get_secret_value(),
            settings.public.algod_address,
        )
        self.validator_multi: MultisigAccount = (
            api_utils.get_validator_account_with_admin(self.acct.addr)
        )
        algo_setup.dev_fund_to_min(
            addr=self.acct.addr,
            min_algos=self.settings.public.ta_validator_funding_threshold_algos + 1,
        )
        LOGGER.info(
            f"mollyMetermaid acct {self.acct.addr_short_hand} balance: {algo_utils.algos(self.acct.addr)} Algos"
        )

        self.seed_fund_validator_joint_account()
        LOGGER.info("DevValidator Initialized")

    #################
    # Messages received
    ################

    def terminalasset_certify_hack_received(
        self, payload: TerminalassetCertifyHack
    ) -> RestfulResponse:
        ta_alias = payload.TerminalAssetAlias
        r = self.post_initial_tadeed_algo_create(ta_alias=ta_alias)
        return r

    ###################
    # Messages sent
    ###################

    def post_initial_tadeed_algo_create(self, ta_alias: str) -> RestfulResponse:
        txn = transaction.AssetCreateTxn(
            sender=self.validator_multi.address(),
            total=1,
            decimals=0,
            default_frozen=False,
            manager=self.settings.public.gnf_admin_addr,
            asset_name=ta_alias,
            unit_name="TADEED",
            sp=self.client.suggested_params(),
        )
        mtx = self.validator_multi.create_mtx(txn)
        mtx.sign(self.acct.sk)

        payload = InitialTadeedAlgoCreate_Maker(
            validator_addr=self.acct.addr,
            half_signed_deed_creation_mtx=encoding.msgpack_encode(mtx),
        ).tuple

        api_endpoint = (
            f"{self.settings.public.gnf_api_root}/initial-tadeed-algo-create/"
        )
        request_response = requests.post(url=api_endpoint, json=payload.as_dict())

        if request_response.status_code > 200:
            if "detail" in request_response.json().keys():
                note = request_response.json()["detail"]
            else:
                note = request_response.reason
            r = RestfulResponse(Note=note, HttpStatusCode=422)
            return r
        r = RestfulResponse(**request_response.json())
        return r

    def post_tavalidatorcert_algo_create(self) -> RestfulResponse:
        txn = transaction.AssetCreateTxn(
            sender=self.validator_multi.address(),
            total=1,
            decimals=0,
            default_frozen=False,
            manager=self.settings.public.gnf_admin_addr,
            asset_name=self.settings.cert_name,
            unit_name="VLDTR",
            note=self.settings.name,
            sp=self.client.suggested_params(),
        )

        mtx = self.validator_multi.create_mtx(txn)
        mtx.sign(self.acct.sk)

        payload = TavalidatorcertAlgoCreate(
            ValidatorAddr=self.acct.addr,
            HalfSignedCertCreationMtx=encoding.msgpack_encode(mtx),
        )
        LOGGER.info("Posting request to GnfRestAPI to create new TaValidatorCert")
        api_endpoint = (
            f"{self.settings.public.gnf_api_root}/tavalidatorcert-algo-create/"
        )

        r = requests.post(url=api_endpoint, json=payload.as_dict())

        if r.status_code > 200:
            LOGGER.warning(r.json())
            if "detail" in r.json().keys():
                note = "TavalidatorcertAlgoCreate error:" + r.json()["detail"]
            else:
                note = r.reason
            return RestfulResponse(Note=note, HttpStatusCode=422)

        rr = RestfulResponse(**r.json())
        cert_idx = rr.PayloadAsDict["Value"]

        payload = self.generate_transfer_tavalidatorcert_algo(cert_idx=cert_idx)

        api_endpoint = (
            f"{self.settings.public.gnf_api_root}/tavalidatorcert-algo-transfer/"
        )
        r = requests.post(url=api_endpoint, json=payload.as_dict())

        if r.status_code > 200:
            if r.status_code == 422:
                note = "TavalidatorcertAlgoTransfer error:" + r.json()["detail"]
            else:
                note = r.reason
            rr = RestfulResponse(Note=note, HttpStatusCode=422)
            return rr

        return RestfulResponse(**r.json())

    def certify_terminal_asset(
        self,
        ta_deed_idx: int,
        ta_daemon_addr: str,
        ta_owner_addr: str,
        micro_lat: int,
        micro_lon: int,
    ) -> RestfulResponse:
        """
        This method is supposed to be called exactly for the FIRST time a TaDeed
        NFT is created for this ta_owner. For updated deeds, uses ExchangeTadeedAlgo

          - Creates the InitialTadeedAlgoTransfer payload and sends it to the Gnf
          - Returns the payload
        Args:
            ta_deed_idx (int): asset id of the TaDeed NFT
            ta_daemon (BasicAccount): The Layer 1 contract supporting NFT ownership
            and creation (TaDeed, TaTradingRights)

        Returns:
            InitialTadeedAlgoTransfer if sent,
            None if ta_multi does not have ta_deed_consideration_algos
        """

        required_algos = config.Public().ta_deed_consideration_algos
        if algo_utils.algos(ta_daemon_addr) < required_algos:
            note = (
                "ta_daemon_addr not sufficiently funded! Has "
                f"{algo_utils.algos(ta_daemon_addr)} Algos and needs "
                f"{required_algos} Algos"
            )
            return RestfulResponse(
                Note=note,
                HttpStatusCode=422,
            )
        txn = transaction.AssetTransferTxn(
            sender=self.validator_multi.addr,
            receiver=ta_daemon_addr,
            amt=1,
            index=ta_deed_idx,
            sp=self.client.suggested_params(),
        )
        mtx = self.validator_multi.create_mtx(txn)
        mtx.sign(self.acct.sk)
        payload = InitialTadeedAlgoTransfer_Maker(
            micro_lat=micro_lat,
            micro_lon=micro_lon,
            validator_addr=self.acct.addr,
            ta_daemon_addr=ta_daemon_addr,
            ta_owner_addr=ta_owner_addr,
            first_deed_transfer_mtx=encoding.msgpack_encode(mtx),
        ).tuple

        api_endpoint = (
            f"{self.settings.public.gnf_api_root}/initial-tadeed-algo-transfer/"
        )
        LOGGER.info(f"Using api_endpoint of {api_endpoint}")
        try:
            r = requests.post(url=api_endpoint, json=payload.as_dict())
        except Exception as e:
            raise Exception(f"DevValidator failed to post request! {e}")

        LOGGER.info("Response from GnfRestAPI:")

        if r.status_code > 200:
            if r.status_code == 422:
                note = "TavalidatorcertAlgoTransfer error:" + r.json()["detail"]
            else:
                note = r.reason
            r = RestfulResponse(Note=note, HttpStatusCode=r.status_code)
            return r

        pprint(r.json())
        r = RestfulResponse(**r.json())
        return r

    def generate_transfer_tavalidatorcert_algo(
        self, cert_idx: int
    ) -> TavalidatorcertAlgoTransfer:
        """First, opts in to the validator cert asset. Then, generates and signs the
        multsig transaction for transfer from the multi account self.multi (joint w
        gnf, threshold 2). Creates the TavalidatorcertAlgoTransferpayload with this
        mtx and sends it to the gnf.

        Args:
            cert_idx (int): the asset index for this validator's cert

        Returns:
            TavalidatorcertAlgoTransfer: the payload sent to the Gnf.
        """

        # Opting in to the cert
        opt_in_txn = transaction.AssetOptInTxn(
            sender=self.acct.addr,
            index=cert_idx,
            sp=self.client.suggested_params(),
        )
        signed_txn = opt_in_txn.sign(self.acct.sk)
        self.client.send_transaction(signed_txn)
        LOGGER.info(f"Molly has opted into asset idx {cert_idx}")
        algo_utils.wait_for_transaction(self.client, signed_txn.get_txid())

        transfer_txn = transaction.AssetTransferTxn(
            sender=self.validator_multi.addr,
            receiver=self.acct.addr,
            amt=1,
            index=cert_idx,
            sp=self.client.suggested_params(),
        )

        mtx = self.validator_multi.create_mtx(transfer_txn)
        mtx.sign(self.acct.sk)

        payload = TavalidatorcertAlgoTransfer(
            ValidatorAddr=self.acct.addr,
            HalfSignedCertTransferMtx=encoding.msgpack_encode(mtx),
        )
        return payload

    ##########################
    # dev methods
    ########################

    def seed_fund_validator_joint_account(
        self,
    ) -> Optional[algo_utils.PendingTxnResponse]:
        """Becoming a validator requires this"""
        required_algos = self.settings.public.ta_validator_funding_threshold_algos
        current_algos = algo_utils.algos(self.validator_multi.address())
        if current_algos >= required_algos:
            LOGGER.info(
                f"ValidatorMulti account already has {current_algos} Algos. No more funding required"
            )
            return
        txn_response = algo_utils.pay_account(
            client=self.client,
            sender=self.acct,
            to_addr=self.validator_multi.address(),
            amt_in_micros=required_algos * 10**6,
        )
        if algo_utils.algos(self.validator_multi.address()) < required_algos:
            raise Exception(
                f"Failed to seed fund validator account {self.validator_multi.address()[-6:]}"
            )
        return txn_response
