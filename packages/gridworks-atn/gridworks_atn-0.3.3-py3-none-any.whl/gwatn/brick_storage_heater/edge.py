""" Heatpumpwithbooststore Flo Edge Class Definition """
from typing import Optional
from typing import no_type_check

from gwatn.data_classes.d_edge import DEdge


SIG_FIGS_FOR_OUTPUT = 6


class Edge__BrickStorageHeater(DEdge):
    def __init__(
        self,
        start_ts_idx: int,
        start_idx: int,
        end_idx: int,
        avg_kw: Optional[float] = None,
        cost: Optional[float] = None,
    ):
        DEdge.__init__(
            self,
            start_ts_idx=start_ts_idx,
            start_idx=start_idx,
            end_idx=end_idx,
            cost=cost,
        )
        self.avg_kw = avg_kw

    def __repr__(self) -> str:
        rep = f"DEdge => Time Slice Idx: {self.start_ts_idx}, StartIdx: {self.start_idx}, EndIdx: {self.end_idx}"
        if self.cost is not None:
            rep += f" Cost => {self.cost}"
        return rep
