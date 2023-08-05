"""Type price.quantity.unitless, version 000"""
import json
from typing import Any
from typing import Dict
from typing import Literal

from gridworks.errors import SchemaError
from pydantic import BaseModel
from pydantic import Field
from pydantic import validator


class PriceQuantityUnitless(BaseModel):
    """ """

    PriceTimes1000: int = Field(
        title="PriceTimes1000",
    )
    QuantityTimes1000: int = Field(
        title="QuantityTimes1000",
    )
    TypeName: Literal["price.quantity.unitless"] = "price.quantity.unitless"
    Version: str = "000"

    def as_dict(self) -> Dict[str, Any]:
        d = self.dict()
        return d

    def as_type(self) -> str:
        return json.dumps(self.as_dict())

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class PriceQuantityUnitless_Maker:
    type_name = "price.quantity.unitless"
    version = "000"

    def __init__(self, price_times1000: int, quantity_times1000: int):
        self.tuple = PriceQuantityUnitless(
            PriceTimes1000=price_times1000,
            QuantityTimes1000=quantity_times1000,
            #
        )

    @classmethod
    def tuple_to_type(cls, tuple: PriceQuantityUnitless) -> str:
        """
        Given a Python class object, returns the serialized JSON type object
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: str) -> PriceQuantityUnitless:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> PriceQuantityUnitless:
        d2 = dict(d)
        if "PriceTimes1000" not in d2.keys():
            raise SchemaError(f"dict {d2} missing PriceTimes1000")
        if "QuantityTimes1000" not in d2.keys():
            raise SchemaError(f"dict {d2} missing QuantityTimes1000")
        if "TypeName" not in d2.keys():
            raise SchemaError(f"dict {d2} missing TypeName")

        return PriceQuantityUnitless(
            PriceTimes1000=d2["PriceTimes1000"],
            QuantityTimes1000=d2["QuantityTimes1000"],
            TypeName=d2["TypeName"],
            Version="000",
        )
