"""Type price.quantity, version 000"""
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

from gwatn.enums import MarketPriceUnit
from gwatn.enums import MarketQuantityUnit


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


class PriceQuantity(BaseModel):
    """ """

    PriceTimes1000: int = Field(
        title="PriceTimes1000",
    )
    QuantityTimes1000: int = Field(
        title="QuantityTimes1000",
    )
    PriceUnit: MarketPriceUnit = Field(
        title="PriceUnit",
    )
    QuantityUnit: MarketQuantityUnit = Field(
        title="QuantityUnit",
    )
    InjectionIsPositive: bool = Field(
        title="InjectionIsPositive",
    )
    TypeName: Literal["price.quantity"] = "price.quantity"
    Version: str = "000"

    @validator("PriceUnit")
    def _check_price_unit(cls, v: MarketPriceUnit) -> MarketPriceUnit:
        return as_enum(v, MarketPriceUnit, MarketPriceUnit.USDPerMWh)

    @validator("QuantityUnit")
    def _check_quantity_unit(cls, v: MarketQuantityUnit) -> MarketQuantityUnit:
        return as_enum(v, MarketQuantityUnit, MarketQuantityUnit.AvgMW)

    def as_dict(self) -> Dict[str, Any]:
        d = self.dict()
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
        return d

    def as_type(self) -> str:
        return json.dumps(self.as_dict())

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class PriceQuantity_Maker:
    type_name = "price.quantity"
    version = "000"

    def __init__(
        self,
        price_times1000: int,
        quantity_times1000: int,
        price_unit: MarketPriceUnit,
        quantity_unit: MarketQuantityUnit,
        injection_is_positive: bool,
    ):
        self.tuple = PriceQuantity(
            PriceTimes1000=price_times1000,
            QuantityTimes1000=quantity_times1000,
            PriceUnit=price_unit,
            QuantityUnit=quantity_unit,
            InjectionIsPositive=injection_is_positive,
            #
        )

    @classmethod
    def tuple_to_type(cls, tuple: PriceQuantity) -> str:
        """
        Given a Python class object, returns the serialized JSON type object
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: str) -> PriceQuantity:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> PriceQuantity:
        d2 = dict(d)
        if "PriceTimes1000" not in d2.keys():
            raise SchemaError(f"dict {d2} missing PriceTimes1000")
        if "QuantityTimes1000" not in d2.keys():
            raise SchemaError(f"dict {d2} missing QuantityTimes1000")
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
        if "InjectionIsPositive" not in d2.keys():
            raise SchemaError(f"dict {d2} missing InjectionIsPositive")
        if "TypeName" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TypeName")

        return PriceQuantity(
            PriceTimes1000=d2["PriceTimes1000"],
            QuantityTimes1000=d2["QuantityTimes1000"],
            PriceUnit=d2["PriceUnit"],
            QuantityUnit=d2["QuantityUnit"],
            InjectionIsPositive=d2["InjectionIsPositive"],
            TypeName=d2["TypeName"],
            Version="000",
        )
