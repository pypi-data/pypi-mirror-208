""" HeatPumpWithBoostStore DNode Definition
"""
from typing import Optional

from gwatn.data_classes.d_node import DNode


SIG_FIGS_FOR_OUTPUT = 6


class Node_BrickStorageHeater(DNode):
    def __init__(
        self,
        ts_idx: int,
        store_idx: int,
        store_enthalpy_kwh: Optional[int] = None,
        store_avg_brick_temp_c: Optional[float] = None,
    ):
        DNode.__init__(
            self,
            ts_idx=ts_idx,
            store_idx=store_idx,
        )
        self.store_enthalpy_kwh = store_enthalpy_kwh
        self.store_avg_brick_temp_c = store_avg_brick_temp_c

    def __repr__(
        self,
    ) -> str:
        rep = f"DNode => TimeSliceIdx: {self.ts_idx}, StoreIdx: {self.store_idx}"
        if self.path_cost:
            rep += f", Path cost: ${round(self.path_cost, 3)}"
        return rep
