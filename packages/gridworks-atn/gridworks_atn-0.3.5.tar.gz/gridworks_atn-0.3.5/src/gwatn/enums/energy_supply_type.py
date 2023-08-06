from enum import auto
from typing import List

from fastapi_utils.enums import StrEnum


class EnergySupplyType(StrEnum):
    """


    Choices and descriptions:

      * Unknown:
      * StandardOffer:
      * RealtimeLocalLmp:
    """

    Unknown = auto()
    StandardOffer = auto()
    RealtimeLocalLmp = auto()

    @classmethod
    def default(cls) -> "EnergySupplyType":
        """
        Returns default value Unknown
        """
        return cls.Unknown

    @classmethod
    def values(cls) -> List[str]:
        """
        Returns enum choices
        """
        return [elt.value for elt in cls]
