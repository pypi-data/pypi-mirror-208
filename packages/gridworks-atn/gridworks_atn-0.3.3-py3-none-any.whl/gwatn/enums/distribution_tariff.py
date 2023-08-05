from enum import auto
from typing import List

from fastapi_utils.enums import StrEnum


class DistributionTariff(StrEnum):
    """
    Name of distribution tariff of local network company/utility

    Choices and descriptions:

      * Unknown:
      * VersantStorageHeatTariff:
      * VersantATariff:
    """

    Unknown = auto()
    VersantStorageHeatTariff = auto()
    VersantATariff = auto()

    @classmethod
    def default(cls) -> "DistributionTariff":
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
