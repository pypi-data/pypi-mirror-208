"""Payload for r.gnode.regp.sync.req.1_0_0"""
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from gwatn.types.gnode_regprequest_ps.r_gnode_regp_sync_req.r_gnode_regp_sync_req_1_0_0_payload_base import (
    PayloadBase,
)


class Payload(PayloadBase):
    def is_valid(self) -> Tuple[bool, Optional[List[str]]]:
        is_valid, errors = self.passes_derived_validations()
        if len(errors) > 0:
            errors.insert(0, "Errors making r.gnode.regp.sync.req.1_0_0 msg.")
        return is_valid, errors

    # hand-code schema axiom validations below
