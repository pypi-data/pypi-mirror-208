import json
from typing import Literal
from typing import Optional

from gwproto.enums import TelemetryName as EnumTelemetryName
from gwproto.errors import MpSchemaError
from gwproto.message import as_enum
from pydantic import BaseModel
from pydantic import Field


class DataChannel(BaseModel):
    """Data Channel.

    A data channel is a concept of some collection of readings that share all characteristics other than time.
    """

    DisplayName: str = Field(
        title="Display Name",
    )
    AboutName: str = Field(
        title="AboutName",
    )
    FromName: str = Field(
        title="FromName",
    )

    TelemetryName: EnumTelemetryName = Field(
        title="TelemetryName",
    )

    ExpectedMaxValue: Optional[int] = Field(title="Expected Max Value, if appropriate")

    ExpectedMinValue: Optional[int] = Field(title="Expected Min Value, if appropriate")

    TypeName: Literal["data.channel"] = "data.channel"
    Version: str = "000"

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa
