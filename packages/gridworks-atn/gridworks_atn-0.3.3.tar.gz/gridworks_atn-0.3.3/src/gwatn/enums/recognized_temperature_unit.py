from enum import auto
from typing import List

from fastapi_utils.enums import StrEnum


class RecognizedTemperatureUnit(StrEnum):
    """
    Unit of temperature

    Choices and descriptions:

      * C: Celcius
      * F: Fahrenheit
    """

    C = auto()
    F = auto()

    @classmethod
    def default(cls) -> "RecognizedTemperatureUnit":
        """
        Returns default value C
        """
        return cls.C

    @classmethod
    def values(cls) -> List[str]:
        """
        Returns enum choices
        """
        return [elt.value for elt in cls]
