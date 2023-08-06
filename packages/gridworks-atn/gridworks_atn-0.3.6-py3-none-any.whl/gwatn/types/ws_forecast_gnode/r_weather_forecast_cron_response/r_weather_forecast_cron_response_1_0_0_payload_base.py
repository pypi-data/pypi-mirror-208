"""PayloadBase for r.weather.forecast.cron.response.1_0_0"""
import datetime
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Tuple

import gwatn.types.hack_property_format as property_format


class PayloadBase(NamedTuple):
    FromGNodeAlias: str  #
    ToGNodeAlias: str  #
    FromGNodeInstanceId: str  #
    BindingKey: str  #
    WorldInstanceAlias: Optional[str] = None
    MpAlias: str = "r.weather.forecast.cron.response.1_0_0"

    def asdict(self):
        d = self._asdict()
        if d["WorldInstanceAlias"] is None:
            del d["WorldInstanceAlias"]
        return d

    def passes_derived_validations(self) -> Tuple[bool, Optional[List[str]]]:
        is_valid = True
        errors = []
        if self.MpAlias != "r.weather.forecast.cron.response.1_0_0":
            is_valid = False
            errors.append(
                f"Payload requires MpAlias of r.weather.forecast.cron.response.1_0_0, not {self.MpAlias}."
            )
        if not isinstance(self.FromGNodeAlias, str):
            is_valid = False
            errors.append(f"FromGNodeAlias {self.FromGNodeAlias} must have type str.")
        if not property_format.is_lrd_alias_format(self.FromGNodeAlias):
            is_valid = False
            errors.append(
                f"FromGNodeAlias {self.FromGNodeAlias} must have format GNodeLrdAliasFormat."
            )
        if not isinstance(self.ToGNodeAlias, str):
            is_valid = False
            errors.append(f"ToGNodeAlias {self.ToGNodeAlias} must have type str.")
        if not property_format.is_lrd_alias_format(self.ToGNodeAlias):
            is_valid = False
            errors.append(
                f"ToGNodeAlias {self.ToGNodeAlias} must have format GNodeLrdAliasFormat."
            )
        if not isinstance(self.FromGNodeInstanceId, str):
            is_valid = False
            errors.append(
                f"FromGNodeInstanceId {self.FromGNodeInstanceId} must have type str."
            )
        if not property_format.is_uuid_canonical_textual(self.FromGNodeInstanceId):
            is_valid = False
            errors.append(
                f"FromGNodeInstanceId {self.FromGNodeInstanceId} must have format UuidCanonicalTextual."
            )
        if not isinstance(self.BindingKey, str):
            is_valid = False
            errors.append(f"BindingKey {self.BindingKey} must have type str.")
        if self.WorldInstanceAlias:
            if not isinstance(self.WorldInstanceAlias, str):
                is_valid = False
                errors.append(
                    f"WorldInstanceAlias {self.WorldInstanceAlias} must have type str."
                )
            if not property_format.is_world_instance_alias_format(
                self.WorldInstanceAlias
            ):
                is_valid = False
                errors.append(
                    f"WorldInstanceAlias {self.WorldInstanceAlias} must have format WorldInstanceAliasFormat"
                )
        return is_valid, errors
