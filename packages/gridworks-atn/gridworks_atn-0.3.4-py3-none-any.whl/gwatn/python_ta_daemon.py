import logging
from typing import List

import dotenv
import gridworks.algo_utils as algo_utils
import gridworks.api_utils as api_utils
from algosdk import encoding
from algosdk.future import transaction
from algosdk.v2client.algod import AlgodClient
from gridworks.algo_utils import BasicAccount
from gridworks.utils import RestfulResponse

import gwatn.config as config
from gwatn.enums import AlgoCertType
from gwatn.types import InitialTadeedAlgoOptin
from gwatn.types import NewTadeedAlgoOptin
from gwatn.types import NewTadeedSend_Maker
from gwatn.types import OldTadeedAlgoReturn
from gwatn.types import SlaEnter


LOGGER = logging.getLogger(__name__)
DUMMY_ACCT_ADDR = "NZXUSTZACPVJBHRSSJ5KE3JUPCITK5P2O4FE67NYPXRDVCJA6ZX4AL62EA"


class PythonTaDaemon:
    def __init__(
        self,
        settings: config.TaDaemonSettings = config.TaDaemonSettings(
            _env_file=dotenv.find_dotenv()
        ),
    ):
        self.settings = settings
        self.client: AlgodClient = AlgodClient(
            settings.algo_api_secrets.algod_token.get_secret_value(),
            settings.public.algod_address,
        )
        self.acct: BasicAccount = BasicAccount(
            private_key=self.settings.sk.get_secret_value()
        )
        self.trading_rights_addr: str = self.acct.addr
        LOGGER.info("TaOwner Smart Daemon Initialized")

    ##########################
    # Messages Received
    ##########################

    def ta_deed_icon_file(self) -> str:
        if self.has_deed():
            return "violet_icon.png"
        else:
            return "not_a_plant.png"

    def initial_tadeed_algo_optin_received(
        self, payload: InitialTadeedAlgoOptin
    ) -> RestfulResponse:
        if self.has_deed():
            r = RestfulResponse(
                Note=f"Ignoring InitialTadeed Optin. Deeds: {self.ta_deed_alias_list}"
            )
            return r
        ta_deed_id = api_utils.get_tadeed_id(
            terminal_asset_alias=payload.TerminalAssetAlias,
            validator_addr=payload.ValidatorAddr,
        )
        if ta_deed_id is None:
            note = f"called when validator {payload.ValidatorAddr[-6:]} did NOT have TADEED for {payload.TerminalAssetAlias}!"
            LOGGER.info(note)
            r = RestfulResponse(
                Note=note,
                HttpStatusCode=422,
            )
            return r
        if ta_deed_id.Type == AlgoCertType.SmartSig:
            raise NotImplementedError(f"Does not yet handle SmartSig TaDeeds")
        # Call a TaDaemonSmartContract method of the same
        # name (InitialTadeedAlgoOptin, in some format)
        # args should include :
        #   - the asset-index
        #   - the TaOwnerAddress
        #   - the TaValidatorAddress
        #
        # the TaDaemonSmartContract should check that:
        #
        #  - That it does not own any assets yet (this is an initial transfer)
        #  - the TaOwnerAddress is its TaOwnerAddress (which it needs to be initialized with)
        #  - the TaValidatorAddress is its TaValidatorAddress (which it needs to be initialized with)
        txn = transaction.AssetOptInTxn(
            sender=self.acct.addr,
            index=ta_deed_id.Idx,
            sp=self.client.suggested_params(),
        )
        signed_txn = txn.sign(self.acct.sk)
        try:
            self.client.send_transaction(signed_txn)
        except:
            return RestfulResponse(
                Note=f"Failure sending transaction to opt into TaDeed {ta_deed_id.Idx}",
                HttpStatusCode=422,
            )
        algo_utils.wait_for_transaction(self.client, signed_txn.get_txid())
        ta_trading_rights_id = api_utils.get_tatrading_rights_id(
            terminal_asset_alias=payload.TerminalAssetAlias
        )
        if ta_trading_rights_id.Type == AlgoCertType.SmartSig:
            raise NotImplementedError(f"Does not yet handle SmartSig TaTradingRights")
        txn = transaction.AssetOptInTxn(
            sender=self.acct.addr,
            index=ta_trading_rights_id.Idx,
            sp=self.client.suggested_params(),
        )
        signed_txn = txn.sign(self.acct.sk)
        try:
            self.client.send_transaction(signed_txn)
        except:
            return RestfulResponse(
                Note=f"Failure sending transaction to opt into TaTradingRights {ta_trading_rights_id.Idx}",
                HttpStatusCode=422,
            )

        note = (
            f"TaDaemon successfully opted in to Initial TaDeed {ta_deed_id.Idx}"
            f" and TaTradingRights {ta_trading_rights_id.Idx}"
        )
        LOGGER.info(note)
        r = RestfulResponse(Note=note)
        return r

    def new_tadeed_algo_optin_received(
        self, payload: NewTadeedAlgoOptin
    ) -> RestfulResponse:
        """Opts in to a new (i.e. updated) TaDeed

        Args:
            payload (NewTadeedAlgoOptin): NewTadeedAlgoOptin

        Returns:
            RestfulResponse:  HttpStatusCode 422 if there is a semantic
            issue (e.g. failure sending transaction on blockchain)

            Otherwise, Payload is NewTadeedSend
        """
        # Call a TaDaemonSmartContract method of the same
        # name (InitialTadeedAlgoOptin, in some format)
        # args should include :
        #   - the asset-index
        #   - the AssetCreatorAddr
        #
        #
        # the TaDaemonSmartContract should check that:
        #
        #  - That it does not own any assets yet (this is an initial transfer)
        #  - the AssetCreatorAddr is "RNMHG32VTIHTC7W3LZOEPTDGREL5IQGK46HKD3KBLZHYQUCAKLMT4G5ALI"
        #        (the GNodeFactory)
        txn = transaction.AssetOptInTxn(
            sender=self.acct.addr,
            index=payload.NewTaDeedIdx,
            sp=self.client.suggested_params(),
        )

        signed_txn = txn.sign(self.acct.sk)
        try:
            self.client.send_transaction(signed_txn)
        except:
            note = "Failure sending transaction on Algo blockchain"
            r = RestfulResponse(
                Note=note,
                HttpStatusCode=422,
            )
            return r
        algo_utils.wait_for_transaction(self.client, signed_txn.get_txid())

        return_payload = NewTadeedSend_Maker(
            new_ta_deed_idx=payload.NewTaDeedIdx,
            old_ta_deed_idx=payload.OldTaDeedIdx,
            ta_daemon_addr=self.acct.addr,
            validator_addr=payload.ValidatorAddr,
            signed_tadeed_optin_txn=encoding.msgpack_encode(signed_txn),
        ).tuple
        note = f"Opted in to TaDeed {payload.NewTaDeedIdx}, ready for transfer"
        r = RestfulResponse(
            Note=note,
            PayloadTypeName=NewTadeedSend_Maker.type_name,
            PayloadAsDict=return_payload.as_dict(),
        )
        LOGGER.info(f"Opted in to TaDeed {payload.NewTaDeedIdx}, ready for transfer")
        return r

    def old_tadeed_algo_return_received(
        self, payload: OldTadeedAlgoReturn
    ) -> RestfulResponse:
        """
         - Transfer the  old deed back to the GNodeFactory admin acct.

        Args:
            payload: OldTadeedAlgoReturn
        """

        # Call a TaDaemonSmartContract method of the same
        # name (OldTadeedAlgoReturn, in some format)
        # args should include :
        #   - the receiver
        #   - the amount
        #    - the asset_index
        # the TaDaemonSmartContract should check
        # that:
        #  - The receiver is "RNMHG32VTIHTC7W3LZOEPTDGREL5IQGK46HKD3KBLZHYQUCAKLMT4G5ALI"
        #  (The GNodeFactory admin address, which it should be initialized with)
        #  - The amount is 1
        #
        txn = transaction.AssetTransferTxn(
            sender=self.acct.addr,
            receiver=config.Public().gnf_admin_addr,
            amt=1,
            index=payload.OldTaDeedIdx,
            sp=self.client.suggested_params(),
        )
        signed_txn = txn.sign(self.acct.sk)
        try:
            self.client.send_transaction(signed_txn)
        except:
            note = "Failure sending transaction on Algo blockchain"
            r = RestfulResponse(
                Note=note,
                HttpStatusCode=422,
            )
            return r

        algo_utils.wait_for_transaction(self.client, signed_txn.get_txid())
        note = f"TaDaemon transferred old TaDeed {payload.OldTaDeedIdx} to GNodeFactoryAdmin"
        LOGGER.info(note)
        r = RestfulResponse(Note=note)
        return r

    def ta_deed_alias_list(self) -> List[str]:
        if self.acct is None:
            return []
        try:
            assets = self.client.account_info(self.acct.addr)["assets"]
        except:
            return []
        owned_assets = list(filter(lambda x: x["amount"] == 1, assets))
        owned_asset_idx_list = list(map(lambda x: x["asset-id"], owned_assets))
        deed_alias_list = []
        for asset_idx in owned_asset_idx_list:
            alias = api_utils.alias_from_deed_idx(asset_idx)
            if alias:
                deed_alias_list.append(alias)
        return deed_alias_list

    def has_deed(self) -> bool:
        if len(self.ta_deed_alias_list()) > 0:
            return True
        return False

    def sla_enter_received(self, payload: SlaEnter) -> RestfulResponse:
        ta_alias = payload.TerminalAssetAlias
        ta_trading_rights_id = api_utils.get_tatrading_rights_id(
            terminal_asset_alias=ta_alias
        )
        if ta_trading_rights_id.Type == AlgoCertType.SmartSig:
            raise NotImplementedError("Does not handle SmartSig TaTradingRights yet")
        alias_list: List[str] = [
            "d1.isone.ver.keene.holly.ta",
            "d1.isone.ver.keene.juniper.ta",
            "d1.isone.ver.keene.kale.ta",
            "d1.isone.ver.keene.lettuce.ta",
        ]

        # These are the secret keys for the 4 demo AtomicTNodes.
        sk_list = [
            "K6iB3AHmzSQ8wDE91QdUfaheDMEtf2WJUMYeeRptKxHiTxG3HC+iKpngXmi82y2r9uVPYwTI5aGiMhdXmPRxcQ==",
            "QfKe/7kzD71nhYGfITlSV/DFYGvC4sc5IEa8ieGsgirC9sBaSJT0O1+mdPOK3/wzZAqy/dRVIg58Uh3ucSIUSw==",
            "UHDv5NTx3pz26XZwpbjwKxmdnYzksEuOmbTbvzgkQbYVnLuK+VLwt0QwgJHAUODoluXS8R5InKOS2X1qNqgBeA==",
            "pMpo89JUKfRE+IvXXW/dsAkns0FXpxagXtQf4m6sXIeO3qH3lHAdbzJvd8gs+xfgnQs3oUs47KD4sWtTARNndw==",
        ]
        if ta_alias not in alias_list:
            return RestfulResponse(
                Note="Did not transfer TaTradingRights, not one of the first 4 atns"
            )
        required_algos = 25

        i = alias_list.index(ta_alias)
        sk = sk_list[i]
        atn_acct = BasicAccount(sk)

        txn = transaction.PaymentTxn(
            sender=self.acct.addr,
            receiver=atn_acct.addr,
            amt=required_algos * 10**6,
            sp=self.client.suggested_params(),
        )
        signed_txn = txn.sign(self.acct.sk)
        try:
            self.client.send_transaction(signed_txn)
        except:
            return RestfulResponse(
                Note=f"Failure Funding {ta_alias} atn",
                HttpStatusCode=422,
            )

        # Hack opt the Atn into the asset using the ATNS PRIVATE KEY.
        # Replace when real SLA exists
        txn = transaction.AssetOptInTxn(
            sender=atn_acct.addr,
            index=ta_trading_rights_id.Idx,
            sp=self.client.suggested_params(),
        )
        signed_txn = txn.sign(atn_acct.sk)
        try:
            self.client.send_transaction(signed_txn)
        except:
            return RestfulResponse(
                Note=f"Atn for {ta_alias} failed to opt into trading rights {ta_trading_rights_id.Idx}",
                HttpStatusCode=422,
            )

        txn = transaction.AssetTransferTxn(
            sender=self.acct.addr,
            receiver=atn_acct.addr,
            amt=1,
            index=ta_trading_rights_id.Idx,
            sp=self.client.suggested_params(),
        )
        signed_txn = txn.sign(self.acct.sk)
        try:
            self.client.send_transaction(signed_txn)
        except:
            note = (
                f"Failure sending AssetTransfer for {ta_alias} trading rights"
                f" {ta_trading_rights_id.Idx}"
            )
            r = RestfulResponse(Note=note, HttpStatusCode=422)
            return r
        self.trading_rights_addr = atn_acct.addr
        return RestfulResponse(
            Note=f"Successfully entered Service Level Agreement for {ta_alias}"
        )
