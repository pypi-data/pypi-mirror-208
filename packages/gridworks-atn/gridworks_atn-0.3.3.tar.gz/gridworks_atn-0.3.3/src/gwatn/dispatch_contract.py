from typing import Final
from typing import Literal

from beaker import Application
from beaker import ApplicationStateValue
from beaker import Authorize
from beaker import close_out
from beaker import create
from beaker import delete
from beaker import external
from beaker import opt_in
from beaker.lib.storage import Mapping
from pyteal import Approve
from pyteal import Assert
from pyteal import AssetHolding
from pyteal import AssetParam
from pyteal import Bytes
from pyteal import Concat
from pyteal import Expr
from pyteal import Global
from pyteal import Int
from pyteal import Seq
from pyteal import TealType
from pyteal import abi


BoxFlatMinBalance = 2500
BoxByteMinBalance = 400


def commented_assert(conditions: list[tuple[Expr, str]]) -> list[Expr]:
    return [Assert(cond, comment=cmt) for cond, cmt in conditions]


class ScadaCertErrors:
    WrongUnitName = "UnitName not SCADA"
    WrongTotal = "Total not 1"
    WrongDecimals = "Decimals not 0"
    WrongManager = "Manager not GnfAdminAddr"
    WrongCreator = "Creator not GnfAdminAddr"


class AtnCertErrors:
    WrongUnitName = "UnitName not TATRADE"
    WrongTotal = "Total not 1"
    WrongDecimals = "Decimals not 0"
    WrongManager = "Manager not GnfAdminAddr"
    WrongCreator = "Creator not GnfAdminAddr"


class DispatchContractErrors:
    ReceiverNotAppAddr = "receiver not app address"
    AmountLessThanMinimum = "amount minimum not met"
    CreatorNotScada = "creator does not own a ScadaCert"
    AtnDoesNotOwnTradingRights = "Atn does not own the correct TaTradingRights"


class HeartbeatB(abi.NamedTuple):
    """Matches GridWorks type heartbeat.b"""

    FromGNodeAlias: abi.Field[abi.String]
    FromGNodeInstanceId: abi.Field[abi.String]
    MyHex: abi.Field[abi.String]
    YourLastHex: abi.Field[abi.String]
    LastReceivedTimeUnixMs: abi.Field[abi.Uint64]
    SendTimeUnixMs: abi.Field[abi.Uint64]
    TypeName: abi.Field[abi.String] = Literal["heartbeat.b"]
    Version: abi.Field[abi.String] = Literal["000"]


class HeartbeatStorageData(abi.NamedTuple):
    """20 bytes of HB Data. Staticly typed for putting into a box"""

    FromScada: abi.Field[abi.Bool]
    MyHex: abi.Field[abi.Byte]
    YourLastHex: abi.Field[abi.Byte]
    LastReceivedTimeUnixMs: abi.Field[abi.Uint64]  # 8 bytes
    SendTimeUnixMs: abi.Field[abi.Uint64]  # 8 bytes


class DispatchContract(Application):
    """The DispatchContract between an AtomicTNode-Scada pair that is coordinating
    the control of their shared TerminalAsset.

    https://gridworks.readthedocs.io/en/latest/dispatch-contract.html
    """

    RecentHeartbeats = Mapping(abi.Uint8, HeartbeatStorageData)
    # RecentHeartbeats = Mapping(abi.StaticBytes[4], HeartbeatData) <- did not work
    # Two rolling hours of minutely HeartbeatData for both Atn and SCADA
    # SCADA keys tagged 0 through 119, Atn keys tagged 120 through 239
    # where the number is minute of day mod 120
    # _heartbeat_box_balance = 4_000_000
    # 2 months of boolean TalkingWith state change, where
    # _talking_with_audit_box_balance = 6_000_000
    # min_balance = _heartbeat_box_balance + _talking_with_audit_box_balance

    min_balance = 10_000_000
    MinimumBalance = Int(min_balance)

    governor: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.bytes,
        default=Global.creator_address(),
        key=Bytes("g"),
        static=True,
        descr="The governor of this contract",
    )

    ta_alias: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.bytes,
        static=True,
        descr="TerminalAsset GNodeAlias",
    )

    scada_cert_idx: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.uint64,
        static=True,
        descr="The asset id of the Scada Cert ASA",
    )

    ta_trading_rights_idx: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.uint64,
        static=True,
        descr="The asset id of the TaTradingRights ASA",
    )

    @external
    def hello(self, name: abi.String, *, output: abi.String):
        """This is in one of the intro beaker vignettes from their
        great set of examples.

        https://github.com/algorand-devrel/beaker/blob/master/examples/simple/hello.py#L8

        Args:
            name: a string

        Returns:
            Hello, name
        """
        return output.set(Concat(Bytes("Hello, "), name.get()))

    @external(authorize=Authorize.only(governor))
    def bootstrap1(
        self,
        scada_seed: abi.PaymentTransaction,
        ScadaCert: abi.Asset,
        *,
        output: abi.String,
    ):
        """First half of the bootstrap. Checks that
           - ScadaCert is valid
           - payment sender (also the governor) owns the ScadaCert, thus proving their
           identity as Scada

            If these checks pass, then the global scada_addr and ta_alias are set.

        Args:
            scada_seed: Initial Payment transaction to the app, by Scada Acct
            ScadaCert: The asset owned by the Scada Addr validating that the GNodeFactory
            authorized its GNode as a SCADA.

        Returns:
            The TerminalAssetAlias (from the ScadaCert)
        """

        return Seq(
            Assert(
                scada_seed.get().receiver() == self.address,
                comment=DispatchContractErrors.ReceiverNotAppAddr,
            ),
            Assert(
                scada_seed.get().amount() >= self.MinimumBalance,
                comment=DispatchContractErrors.AmountLessThanMinimum,
            ),
            cert_type := AssetParam.unitName(ScadaCert.asset_id()),
            Assert(cert_type.hasValue()),
            Assert(
                cert_type.value() == Bytes("SCADA"),
                comment=ScadaCertErrors.WrongUnitName,
            ),
            ta_alias := AssetParam.name(ScadaCert.asset_id()),
            Assert(ta_alias.hasValue()),
            scada_cert_balance := AssetHolding.balance(
                scada_seed.get().sender(), ScadaCert.asset_id()
            ),
            Assert(scada_cert_balance.hasValue()),
            Assert(
                scada_cert_balance.value() == Int(1),
                comment=DispatchContractErrors.CreatorNotScada,
            ),
            # creator := AssetParam.creator(ScadaCert.asset_id()),
            # Assert(creator.hasValue()),
            # Assert(
            #     creator.value() == config.Public().gnf_admin_addr,
            #     comment=ScadaCertErrors.WrongCreator,
            # ),
            # manager := AssetParam.manager(ScadaCert.asset_id()),
            # Assert(manager.hasValue()),
            # Assert(
            #     manager.value() == config.Public().gnf_admin_addr,
            #     comment=ScadaCertErrors.WrongManager,
            # ),
            self.scada_cert_idx.set(ScadaCert.asset_id()),
            self.ta_alias.set(ta_alias.value()),
            output.set(ta_alias.value()),
        )

    @external
    def bootstrap2(
        self,
        atn_seed: abi.PaymentTransaction,
        TaTradingRights: abi.Asset,
        *,
        output: abi.String,
    ):
        """
        "Second half of the bootstrap, done by Atn calling this method. Method checks that
           - TaTradingRights are valid, and match the global
           ta_alias (which must already exist)
           - Atn payment meets the MinimumBalance requirements of the DispatchContract
           - payment sender owns the TaTradingRights, thus proving their
           identity as AtomicTNode

            https://gridworks.readthedocs.io/en/latest/ta-trading-rights.html
            If these checks pass, then the global atn_addr is set.

        Args:
            atn_seed: Initial Payment transaction to the app from Atn. This pays for boxes.
            TaTradingRights: The asset owned by the Atn Addr validating is right to trade
            energy on behalf of the TerminalAsset

        Returns:
            The TerminalAssetAlias
        """
        return Seq(
            Assert(
                atn_seed.get().receiver() == self.address,
                comment=DispatchContractErrors.ReceiverNotAppAddr,
            ),
            cert_type := AssetParam.unitName(TaTradingRights.asset_id()),
            Assert(cert_type.hasValue()),
            Assert(
                cert_type.value() == Bytes("TATRADE"),
                comment=AtnCertErrors.WrongUnitName,
            ),
            ta_alias := AssetParam.name(TaTradingRights.asset_id()),
            Assert(ta_alias.hasValue()),
            Assert(self.ta_alias == ta_alias.value()),
            atn_cert_balance := AssetHolding.balance(
                atn_seed.get().sender(), TaTradingRights.asset_id()
            ),
            Assert(
                atn_cert_balance.hasValue(),
                comment=DispatchContractErrors.AtnDoesNotOwnTradingRights,
            ),
            Assert(
                atn_cert_balance.value() == Int(1),
                comment=DispatchContractErrors.AtnDoesNotOwnTradingRights,
            ),
            self.ta_trading_rights_idx.set(TaTradingRights.asset_id()),
            output.set(self.ta_alias),
        )

    @external
    def get_ta_alias(self, *, output: abi.String):
        """
        Returns the GNodeAlias of the TerminalAsset for the Dispatch Contract.
        https://gridworks.readthedocs.io/en/latest/g-node-alias.html
        https://gridworks.readthedocs.io/en/latest/terminal-asset.html

        Returns:
            TerminalAsset GNodeAlias
        """
        return Seq(
            output.set(self.ta_alias.get()),
        )

    @create
    def create(self):
        return self.initialize_application_state()

    @opt_in
    def opt_in(self):
        """Address opting in must be either scada_addr or atn_addr"""
        # Todo: figure out how to get the address opting in
        return self.initialize_account_state()

    @external(authorize=Authorize.opted_in())
    def heartbeat_algo_audit(
        self,
        signed_proof: abi.PaymentTransaction,
        heartbeat: HeartbeatB,
        *,
        output: abi.String,
    ):
        """
        What: Algo payload with report of last HeartbeatB sent to partner via Rabbit, to be sent to
        DispatchContract on Algo blockchain

        Why: After validating the identity of the sender by inspecting the signed_proof, the
        DispatchContract shortens up the heartbeat info into the more compact form of
        HeartbeatStorageData, and stores in a box. Two hours of the most recent minutely heartbeats are
        stored, using one box for recent Atn heartbeats and one box for recent Scada heartbeats.

        See https://gridworks-atn.readthedocs.io/en/latest/apis/types.html#heartbeatalgoaudit

        Args:
            signed_proof: Tiny signed payment to DispatchContract to prove identity
            heartbeat: Heartbeat sender last sent to its partner
            See https://gridworks-atn.readthedocs.io/en/latest/apis/types.html#heartbeatb
        """
        return Seq(
            output.set(self.ta_alias.get()),
        )

    @close_out
    def close_out(self):
        return Approve()

    @delete(authorize=Authorize.only(governor))
    def delete(self):
        return Approve()


if __name__ == "__main__":
    DispatchContract().dump("dispatch_contract_artifacts")
