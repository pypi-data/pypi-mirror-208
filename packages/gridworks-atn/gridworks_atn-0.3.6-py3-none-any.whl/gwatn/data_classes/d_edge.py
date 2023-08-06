""" DEdege (Dijkstra Edge) Class Definition """
from abc import ABC
from typing import Optional


class DEdge(ABC):
    def __init__(
        self,
        start_ts_idx: int,
        start_idx: int,
        end_idx: int,
        cost: Optional[float] = None,
    ):
        self.start_ts_idx = start_ts_idx
        self.start_idx = start_idx
        self.end_idx = end_idx
        self.cost = cost

    def __repr__(self) -> str:
        return f"DEdge => StartTimeSliceIdx: {self.start_ts_idx}. StartStoreIdx: {self.start_idx}. EndStoreIdx: {self.end_idx}. Cost: {self.cost}"
