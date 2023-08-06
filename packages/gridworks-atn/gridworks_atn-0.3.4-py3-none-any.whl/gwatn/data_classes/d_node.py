""" DNode (Dijkstra Node) Definition """
from abc import ABC
from typing import Optional


SIG_FIGS_FOR_OUTPUT = 6


class DNode(ABC):
    SIG_FIGS_FOR_OUTPUT = 6

    def __init__(
        self,
        ts_idx: int,
        store_idx: int,
        local_benefit: float = 0,
    ):
        self.ts_idx = ts_idx
        self.store_idx = store_idx
        self.local_benefit = local_benefit
        self.path_benefit: Optional[float] = None
        self.best_next_idx: Optional[int] = None
        self.path_edge_cost_only: Optional[float] = None

    @property
    def path_cost(self) -> Optional[float]:
        if self.path_benefit is None:
            return None
        return -self.path_benefit

    def __repr__(self) -> str:
        if self.local_benefit:
            local_benefit = round(self.local_benefit, self.SIG_FIGS_FOR_OUTPUT)
        else:
            local_benefit = None
        if self.path_benefit:
            path_benefit = round(self.path_benefit, self.SIG_FIGS_FOR_OUTPUT)
        else:
            path_benefit = None
        if self.path_edge_cost_only:
            path_edge_cost_only = round(
                self.path_edge_cost_only, self.SIG_FIGS_FOR_OUTPUT
            )
        else:
            path_edge_cost_only = None
        return (
            f"DNode => TsIdx: {self.ts_idx}, StoreIdx: {self.store_idx}, BestNextIdx: {self.best_next_idx}, "
            f"LocalBenefit: {local_benefit}, PathBenefit: {path_benefit}, PathEdgeCostOnly: {path_edge_cost_only}"
        )
