from enum import auto
from typing import List

from fastapi_utils.enums import StrEnum


class RecognizedIrradianceType(StrEnum):
    """


    Choices and descriptions:

      * PlaneOfArray: The sum of the direct normal (DNI) and diffuse (DHI) irradiance components incident on a surface with a given tilt and angle of incidence (AOI)
      * Hor: Also known as Global Horizontal Irradiance (GHI), this is the total solar radiation incident on a horizontal surface. It is the sum of Direct Normal Irradiance (DNI), Diffuse Horizontal Irradiance, and ground-reflected radiation
    """

    PlaneOfArray = auto()
    Hor = auto()

    @classmethod
    def default(cls) -> "RecognizedIrradianceType":
        """
        Returns default value PlaneOfArray
        """
        return cls.PlaneOfArray

    @classmethod
    def values(cls) -> List[str]:
        """
        Returns enum choices
        """
        return [elt.value for elt in cls]
