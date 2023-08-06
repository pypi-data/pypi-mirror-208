"""Type market.type.gt, version 000"""
import json
from enum import auto
from typing import Any
from typing import Dict
from typing import List
from typing import Literal

from fastapi_utils.enums import StrEnum
from gridworks.errors import SchemaError
from gridworks.message import as_enum
from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from gwatn.data_classes import MarketType
from gwatn.enums import MarketPriceUnit
from gwatn.enums import MarketQuantityUnit
from gwatn.enums import MarketTypeName
from gwatn.enums import RecognizedCurrencyUnit


class MarketPriceUnit000SchemaEnum:
    enum_name: str = "market.price.unit.000"
    symbols: List[str] = [
        "00000000",
    ]

    @classmethod
    def is_symbol(cls, candidate: str) -> bool:
        if candidate in cls.symbols:
            return True
        return False


class MarketPriceUnit000(StrEnum):
    USDPerMWh = auto()

    @classmethod
    def default(cls) -> "MarketPriceUnit000":
        return cls.USDPerMWh

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]


class MarketPriceUnitMap:
    @classmethod
    def type_to_local(cls, symbol: str) -> MarketPriceUnit:
        if not MarketPriceUnit000SchemaEnum.is_symbol(symbol):
            raise SchemaError(f"{symbol} must belong to MarketPriceUnit000 symbols")
        versioned_enum = cls.type_to_versioned_enum_dict[symbol]
        return as_enum(versioned_enum, MarketPriceUnit, MarketPriceUnit.default())

    @classmethod
    def local_to_type(cls, market_price_unit: MarketPriceUnit) -> str:
        if not isinstance(market_price_unit, MarketPriceUnit):
            raise SchemaError(f"{market_price_unit} must be of type {MarketPriceUnit}")
        versioned_enum = as_enum(
            market_price_unit, MarketPriceUnit000, MarketPriceUnit000.default()
        )
        return cls.versioned_enum_to_type_dict[versioned_enum]

    type_to_versioned_enum_dict: Dict[str, MarketPriceUnit000] = {
        "00000000": MarketPriceUnit000.USDPerMWh,
    }

    versioned_enum_to_type_dict: Dict[MarketPriceUnit000, str] = {
        MarketPriceUnit000.USDPerMWh: "00000000",
    }


class RecognizedCurrencyUnit000SchemaEnum:
    enum_name: str = "recognized.currency.unit.000"
    symbols: List[str] = [
        "00000000",
        "e57c5143",
        "f7b38fc5",
    ]

    @classmethod
    def is_symbol(cls, candidate: str) -> bool:
        if candidate in cls.symbols:
            return True
        return False


class RecognizedCurrencyUnit000(StrEnum):
    UNKNOWN = auto()
    USD = auto()
    GBP = auto()

    @classmethod
    def default(cls) -> "RecognizedCurrencyUnit000":
        return cls.UNKNOWN

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]


class RecognizedCurrencyUnitMap:
    @classmethod
    def type_to_local(cls, symbol: str) -> RecognizedCurrencyUnit:
        if not RecognizedCurrencyUnit000SchemaEnum.is_symbol(symbol):
            raise SchemaError(
                f"{symbol} must belong to RecognizedCurrencyUnit000 symbols"
            )
        versioned_enum = cls.type_to_versioned_enum_dict[symbol]
        return as_enum(
            versioned_enum, RecognizedCurrencyUnit, RecognizedCurrencyUnit.default()
        )

    @classmethod
    def local_to_type(cls, recognized_currency_unit: RecognizedCurrencyUnit) -> str:
        if not isinstance(recognized_currency_unit, RecognizedCurrencyUnit):
            raise SchemaError(
                f"{recognized_currency_unit} must be of type {RecognizedCurrencyUnit}"
            )
        versioned_enum = as_enum(
            recognized_currency_unit,
            RecognizedCurrencyUnit000,
            RecognizedCurrencyUnit000.default(),
        )
        return cls.versioned_enum_to_type_dict[versioned_enum]

    type_to_versioned_enum_dict: Dict[str, RecognizedCurrencyUnit000] = {
        "00000000": RecognizedCurrencyUnit000.UNKNOWN,
        "e57c5143": RecognizedCurrencyUnit000.USD,
        "f7b38fc5": RecognizedCurrencyUnit000.GBP,
    }

    versioned_enum_to_type_dict: Dict[RecognizedCurrencyUnit000, str] = {
        RecognizedCurrencyUnit000.UNKNOWN: "00000000",
        RecognizedCurrencyUnit000.USD: "e57c5143",
        RecognizedCurrencyUnit000.GBP: "f7b38fc5",
    }


class MarketTypeName000SchemaEnum:
    enum_name: str = "market.type.name.000"
    symbols: List[str] = [
        "00000000",
        "d20b81e4",
        "b36cbfb4",
        "94a3fe9b",
        "5f335bdb",
        "01a84101",
        "e997ccfb",
        "618f9c0a",
    ]

    @classmethod
    def is_symbol(cls, candidate: str) -> bool:
        if candidate in cls.symbols:
            return True
        return False


class MarketTypeName000(StrEnum):
    unknown = auto()
    rt5gate5 = auto()
    rt60gate5 = auto()
    da60 = auto()
    rt60gate30 = auto()
    rt15gate5 = auto()
    rt30gate5 = auto()
    rt60gate30b = auto()

    @classmethod
    def default(cls) -> "MarketTypeName000":
        return cls.unknown

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]


class MarketTypeNameMap:
    @classmethod
    def type_to_local(cls, symbol: str) -> MarketTypeName:
        if not MarketTypeName000SchemaEnum.is_symbol(symbol):
            raise SchemaError(f"{symbol} must belong to MarketTypeName000 symbols")
        versioned_enum = cls.type_to_versioned_enum_dict[symbol]
        return as_enum(versioned_enum, MarketTypeName, MarketTypeName.default())

    @classmethod
    def local_to_type(cls, market_type_name: MarketTypeName) -> str:
        if not isinstance(market_type_name, MarketTypeName):
            raise SchemaError(f"{market_type_name} must be of type {MarketTypeName}")
        versioned_enum = as_enum(
            market_type_name, MarketTypeName000, MarketTypeName000.default()
        )
        return cls.versioned_enum_to_type_dict[versioned_enum]

    type_to_versioned_enum_dict: Dict[str, MarketTypeName000] = {
        "00000000": MarketTypeName000.unknown,
        "d20b81e4": MarketTypeName000.rt5gate5,
        "b36cbfb4": MarketTypeName000.rt60gate5,
        "94a3fe9b": MarketTypeName000.da60,
        "5f335bdb": MarketTypeName000.rt60gate30,
        "01a84101": MarketTypeName000.rt15gate5,
        "e997ccfb": MarketTypeName000.rt30gate5,
        "618f9c0a": MarketTypeName000.rt60gate30b,
    }

    versioned_enum_to_type_dict: Dict[MarketTypeName000, str] = {
        MarketTypeName000.unknown: "00000000",
        MarketTypeName000.rt5gate5: "d20b81e4",
        MarketTypeName000.rt60gate5: "b36cbfb4",
        MarketTypeName000.da60: "94a3fe9b",
        MarketTypeName000.rt60gate30: "5f335bdb",
        MarketTypeName000.rt15gate5: "01a84101",
        MarketTypeName000.rt30gate5: "e997ccfb",
        MarketTypeName000.rt60gate30b: "618f9c0a",
    }


class MarketQuantityUnit000SchemaEnum:
    enum_name: str = "market.quantity.unit.000"
    symbols: List[str] = [
        "00000000",
        "c272f3b3",
    ]

    @classmethod
    def is_symbol(cls, candidate: str) -> bool:
        if candidate in cls.symbols:
            return True
        return False


class MarketQuantityUnit000(StrEnum):
    AvgMW = auto()
    AvgkW = auto()

    @classmethod
    def default(cls) -> "MarketQuantityUnit000":
        return cls.AvgMW

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]


class MarketQuantityUnitMap:
    @classmethod
    def type_to_local(cls, symbol: str) -> MarketQuantityUnit:
        if not MarketQuantityUnit000SchemaEnum.is_symbol(symbol):
            raise SchemaError(f"{symbol} must belong to MarketQuantityUnit000 symbols")
        versioned_enum = cls.type_to_versioned_enum_dict[symbol]
        return as_enum(versioned_enum, MarketQuantityUnit, MarketQuantityUnit.default())

    @classmethod
    def local_to_type(cls, market_quantity_unit: MarketQuantityUnit) -> str:
        if not isinstance(market_quantity_unit, MarketQuantityUnit):
            raise SchemaError(
                f"{market_quantity_unit} must be of type {MarketQuantityUnit}"
            )
        versioned_enum = as_enum(
            market_quantity_unit, MarketQuantityUnit000, MarketQuantityUnit000.default()
        )
        return cls.versioned_enum_to_type_dict[versioned_enum]

    type_to_versioned_enum_dict: Dict[str, MarketQuantityUnit000] = {
        "00000000": MarketQuantityUnit000.AvgMW,
        "c272f3b3": MarketQuantityUnit000.AvgkW,
    }

    versioned_enum_to_type_dict: Dict[MarketQuantityUnit000, str] = {
        MarketQuantityUnit000.AvgMW: "00000000",
        MarketQuantityUnit000.AvgkW: "c272f3b3",
    }


class MarketTypeGt(BaseModel):
    """Used by MarketMakers to simultaneously run several different types of Markets.

        A [MarketMaker](https://gridworks.readthedocs.io/en/latest/market-maker.html) GNode can run several types of Markets. For example, it can run an
    hourly real-time market and also an ancillary services market for Regulation. This is captured
    by the concept of MarketType.
        [More info](https://gridworks.readthedocs.io/en/latest/market-type.html).
    """

    Name: MarketTypeName = Field(
        title="Name of the MarketType",
    )
    DurationMinutes: int = Field(
        title="Duration of MarketSlots, in minutes",
    )
    GateClosingSeconds: int = Field(
        title="Seconds before the start of a MarketSlot after which bids are not accepted",
    )
    PriceUnit: MarketPriceUnit = Field(
        title="Price Unit for market (e.g. USD Per MWh)",
    )
    QuantityUnit: MarketQuantityUnit = Field(
        title="Quantity Unit for market (e.g. AvgMW)",
    )
    CurrencyUnit: RecognizedCurrencyUnit = Field(
        title="Currency Unit for market (e.g. USD)",
    )
    PriceMax: int = Field(
        title="PMax, required for defining bids",
    )
    TypeName: Literal["market.type.gt"] = "market.type.gt"
    Version: str = "000"

    @validator("Name")
    def _check_name(cls, v: MarketTypeName) -> MarketTypeName:
        return as_enum(v, MarketTypeName, MarketTypeName.unknown)

    @validator("PriceUnit")
    def _check_price_unit(cls, v: MarketPriceUnit) -> MarketPriceUnit:
        return as_enum(v, MarketPriceUnit, MarketPriceUnit.USDPerMWh)

    @validator("QuantityUnit")
    def _check_quantity_unit(cls, v: MarketQuantityUnit) -> MarketQuantityUnit:
        return as_enum(v, MarketQuantityUnit, MarketQuantityUnit.AvgMW)

    @validator("CurrencyUnit")
    def _check_currency_unit(cls, v: RecognizedCurrencyUnit) -> RecognizedCurrencyUnit:
        return as_enum(v, RecognizedCurrencyUnit, RecognizedCurrencyUnit.UNKNOWN)

    def as_dict(self) -> Dict[str, Any]:
        d = self.dict()
        del d["Name"]
        Name = as_enum(self.Name, MarketTypeName, MarketTypeName.default())
        d["NameGtEnumSymbol"] = MarketTypeNameMap.local_to_type(Name)
        del d["PriceUnit"]
        PriceUnit = as_enum(self.PriceUnit, MarketPriceUnit, MarketPriceUnit.default())
        d["PriceUnitGtEnumSymbol"] = MarketPriceUnitMap.local_to_type(PriceUnit)
        del d["QuantityUnit"]
        QuantityUnit = as_enum(
            self.QuantityUnit, MarketQuantityUnit, MarketQuantityUnit.default()
        )
        d["QuantityUnitGtEnumSymbol"] = MarketQuantityUnitMap.local_to_type(
            QuantityUnit
        )
        del d["CurrencyUnit"]
        CurrencyUnit = as_enum(
            self.CurrencyUnit, RecognizedCurrencyUnit, RecognizedCurrencyUnit.default()
        )
        d["CurrencyUnitGtEnumSymbol"] = RecognizedCurrencyUnitMap.local_to_type(
            CurrencyUnit
        )
        return d

    def as_type(self) -> str:
        return json.dumps(self.as_dict())

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class MarketTypeGt_Maker:
    type_name = "market.type.gt"
    version = "000"

    def __init__(
        self,
        name: MarketTypeName,
        duration_minutes: int,
        gate_closing_seconds: int,
        price_unit: MarketPriceUnit,
        quantity_unit: MarketQuantityUnit,
        currency_unit: RecognizedCurrencyUnit,
        price_max: int,
    ):
        self.tuple = MarketTypeGt(
            Name=name,
            DurationMinutes=duration_minutes,
            GateClosingSeconds=gate_closing_seconds,
            PriceUnit=price_unit,
            QuantityUnit=quantity_unit,
            CurrencyUnit=currency_unit,
            PriceMax=price_max,
            #
        )

    @classmethod
    def tuple_to_type(cls, tuple: MarketTypeGt) -> str:
        """
        Given a Python class object, returns the serialized JSON type object
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: str) -> MarketTypeGt:
        """
        Given a serialized JSON type object, returns the Python class object
        """
        try:
            d = json.loads(t)
        except TypeError:
            raise SchemaError("Type must be string or bytes!")
        if not isinstance(d, dict):
            raise SchemaError(f"Deserializing {t} must result in dict!")
        return cls.dict_to_tuple(d)

    @classmethod
    def dict_to_tuple(cls, d: dict[str, Any]) -> MarketTypeGt:
        d2 = dict(d)
        if "NameGtEnumSymbol" not in d2.keys():
            raise SchemaError(f"dict {d2} missing NameGtEnumSymbol")
        if d2["NameGtEnumSymbol"] in MarketTypeName000SchemaEnum.symbols:
            d2["Name"] = MarketTypeNameMap.type_to_local(d2["NameGtEnumSymbol"])
        else:
            d2["Name"] = MarketTypeName.default()
        if "DurationMinutes" not in d2.keys():
            raise SchemaError(f"dict {d2} missing DurationMinutes")
        if "GateClosingSeconds" not in d2.keys():
            raise SchemaError(f"dict {d2} missing GateClosingSeconds")
        if "PriceUnitGtEnumSymbol" not in d2.keys():
            raise SchemaError(f"dict {d2} missing PriceUnitGtEnumSymbol")
        if d2["PriceUnitGtEnumSymbol"] in MarketPriceUnit000SchemaEnum.symbols:
            d2["PriceUnit"] = MarketPriceUnitMap.type_to_local(
                d2["PriceUnitGtEnumSymbol"]
            )
        else:
            d2["PriceUnit"] = MarketPriceUnit.default()
        if "QuantityUnitGtEnumSymbol" not in d2.keys():
            raise SchemaError(f"dict {d2} missing QuantityUnitGtEnumSymbol")
        if d2["QuantityUnitGtEnumSymbol"] in MarketQuantityUnit000SchemaEnum.symbols:
            d2["QuantityUnit"] = MarketQuantityUnitMap.type_to_local(
                d2["QuantityUnitGtEnumSymbol"]
            )
        else:
            d2["QuantityUnit"] = MarketQuantityUnit.default()
        if "CurrencyUnitGtEnumSymbol" not in d2.keys():
            raise SchemaError(f"dict {d2} missing CurrencyUnitGtEnumSymbol")
        if (
            d2["CurrencyUnitGtEnumSymbol"]
            in RecognizedCurrencyUnit000SchemaEnum.symbols
        ):
            d2["CurrencyUnit"] = RecognizedCurrencyUnitMap.type_to_local(
                d2["CurrencyUnitGtEnumSymbol"]
            )
        else:
            d2["CurrencyUnit"] = RecognizedCurrencyUnit.default()
        if "PriceMax" not in d2.keys():
            raise SchemaError(f"dict {d2} missing PriceMax")
        if "TypeName" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TypeName")

        return MarketTypeGt(
            Name=d2["Name"],
            DurationMinutes=d2["DurationMinutes"],
            GateClosingSeconds=d2["GateClosingSeconds"],
            PriceUnit=d2["PriceUnit"],
            QuantityUnit=d2["QuantityUnit"],
            CurrencyUnit=d2["CurrencyUnit"],
            PriceMax=d2["PriceMax"],
            TypeName=d2["TypeName"],
            Version="000",
        )

    @classmethod
    def tuple_to_dc(cls, t: MarketTypeGt) -> MarketType:
        if t.Name in MarketType.by_id.keys():
            dc = MarketType.by_id[t.Name]
        else:
            dc = MarketType(
                name=t.Name,
                duration_minutes=t.DurationMinutes,
                gate_closing_seconds=t.GateClosingSeconds,
                price_unit=t.PriceUnit,
                quantity_unit=t.QuantityUnit,
                currency_unit=t.CurrencyUnit,
                price_max=t.PriceMax,
            )

        return dc

    @classmethod
    def dc_to_tuple(cls, dc: MarketType) -> MarketTypeGt:
        t = MarketTypeGt_Maker(
            name=dc.name,
            duration_minutes=dc.duration_minutes,
            gate_closing_seconds=dc.gate_closing_seconds,
            price_unit=dc.price_unit,
            quantity_unit=dc.quantity_unit,
            currency_unit=dc.currency_unit,
            price_max=dc.price_max,
        ).tuple
        return t

    @classmethod
    def type_to_dc(cls, t: str) -> MarketType:
        return cls.tuple_to_dc(cls.type_to_tuple(t))

    @classmethod
    def dc_to_type(cls, dc: MarketType) -> str:
        return cls.dc_to_tuple(dc).as_type()

    @classmethod
    def dict_to_dc(cls, d: dict[Any, str]) -> MarketType:
        return cls.tuple_to_dc(cls.dict_to_tuple(d))
