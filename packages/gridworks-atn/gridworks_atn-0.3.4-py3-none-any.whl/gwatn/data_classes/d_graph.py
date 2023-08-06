# type: ignore
import time
from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

import pendulum
import pytz

from gwatn.data_classes import DEdge
from gwatn.data_classes import DNode
from gwatn.enums import RecognizedCurrencyUnit


class Edges:
    """A doubly indexed dict of DEDges"""

    as_dict: Dict[int, Dict[int, DEdge]]

    def __repr__(self) -> str:
        return (
            "calling as_dict returns a double dictionary of edges from a Node  \n"
            "with first key of the start_ts_idx of the Node and second key of start_idx"
        )


class DGraph(ABC):
    def __init__(
        self,
        d_graph_id: str,
        graph_strategy_alias: str,
        flo_start_unix_time_s: int,
        slice_duration_hrs: List[float],
        timezone_string: str,
        default_storage_steps: int,
        starting_store_idx: int,
        home_city: str,
        currency_unit: RecognizedCurrencyUnit,
        max_storage: float,
        max_power_in: float,
        wh_exponent: int = 3,
    ):
        self.graph_strategy_alias = graph_strategy_alias
        self.starting_store_idx = starting_store_idx
        self.edges: Dict[
            DNode, List[DEdge]
        ] = (
            {}
        )  # a dictionary that takes nodes to lists of edges connecting that node to nodes in the next time slice
        self.best_edge: Dict[
            DNode, DEdge
        ] = {}  # a dictionary that takes node to its best edge in the dijsktra path
        self.node: Dict[
            int, Dict[int, DNode]
        ] = (
            {}
        )  # self.node[jj][kk] is the node with time slice index jj and energy index kk
        self.slice_duration_hrs = slice_duration_hrs
        self.time_slices: int = len(self.slice_duration_hrs)
        self.default_storage_steps = default_storage_steps
        self.storage_steps: Dict[int, int] = {}
        self.set_storage_steps_per_time_slice()
        self.flo_start_unix_time_s: int = flo_start_unix_time_s
        self.timezone_string: str = timezone_string
        self.validate_timezone_format()
        self.flo_start_utc: Any = pendulum.from_timestamp(self.flo_start_unix_time_s)
        self.slice_start_utc: Dict[int, Any] = {}
        self.slice_start_unix_seconds: Dict[int, int] = {}
        self.set_slice_start()

        self.home_city = home_city
        self.currency_unit = currency_unit
        self.max_storage = max_storage
        self.max_power_in = max_power_in
        self.wh_exponent = wh_exponent
        self.d_graph_id = d_graph_id

    def __repr__(self) -> str:
        return f"Flo: Starting node: {self.node[0][self.starting_store_idx]}. Try flo.edges[flo.node[0][flo.starting_idx]"

    def validate_timezone_format(self) -> None:
        if not self.timezone_string in pytz.all_timezones:
            raise Exception(
                f"self.timezone_string '{self.timezone_string}' is not in the list of pytz.all_timezones"
            )

    @abstractmethod
    def create_graph(self) -> None:
        """The Dijsktra graph has nodes indexed first by
        time_slice_idx (range(self.time_slices)) and then by
        store_idx (range(self.store_steps[time_slice_idx])).
        The edges are always between nodes in adjacent time_slices,
        and reflect the potential future state changes that could
        occur. Each edge is, importantly, assigned an edge cost. In
        addition nodes can have `local benefits` (i.e. negative costs).

        Building this graph takes more time than solving for the
        lowest-cost path through the graph - which is Dijsktra's
        algorithm.

        Raises:
            NotImplementedError: This method is expected to
            be created by individual flos
        """
        raise NotImplementedError

    def set_final_slice_benefits(self) -> None:
        for node in self.node[self.time_slices].values():
            node.path_benefit = node.local_benefit
            node.path_edge_cost_only = 0

    def solve_dijkstra(self) -> None:
        st = time.time()
        # print("Solving dijkstra")
        self.set_final_slice_benefits()
        last_bad_slice_found = False
        for mm in range(1, self.time_slices + 1):
            # start from the last time slice and work to the front
            ts_idx = self.time_slices - mm
            bad_slice = True
            for node in self.node[ts_idx].values():
                edges = self.edges[node]
                # options gives a list of edge choices along with the cost of the path
                # from the node assuming that this edge is chosen, and that from that point
                # on the optimal path is chosen.

                # The path cost is the sum of the local cost at the current node, the
                # edge cost of the edge choice, and the path cost of the node in the next
                # time slice.
                try:
                    options = list(
                        map(
                            lambda x: [
                                x,
                                self.node[ts_idx + 1][x.end_idx].path_benefit
                                + self.node[ts_idx][x.start_idx].local_benefit
                                - x.cost,
                            ],
                            edges,
                        )
                    )
                except:
                    raise Exception(f"failed for node {node}")
                try:
                    best: Tuple[int, DEdge] = max(options, key=lambda x: x[1])
                except ValueError:
                    raise Exception(f"trouble with node {node}")

                best_edge: DEdge = best[0]
                self.best_edge[node]: DEdge = best_edge

                node.path_benefit = best[1]
                best_next_node = self.node[ts_idx + 1][best_edge.end_idx]
                node.best_next_idx = best_next_node.store_idx
                node.path_edge_cost_only = (
                    best_edge.cost + best_next_node.path_edge_cost_only
                )
                if node.path_cost < 10**5:
                    bad_slice = False

            if bad_slice is True and last_bad_slice_found is False:
                # print(f"last bad slice found: {ts_idx}")
                last_bad_slice_found = True
        # print(f"Total time for solving dijkstra:{1000*(time.time() - st):2.0f} ms ")

    def set_storage_steps_per_time_slice(self) -> None:
        """Initialize the dictionary self.store_steps.
        The keys are range(self.time_slices) and the values
        are the number of storage steps (e.g. how many
        ESteps) at the beginning of that time slice.

        This can be overwritten by inheriting classes
        """
        for jj in range(self.time_slices):
            self.storage_steps[jj] = self.default_storage_steps

    def set_slice_start(self) -> None:
        sd = self.flo_start_utc
        self.slice_start_utc[0] = sd
        self.slice_start_unix_seconds[0] = int(sd.timestamp())
        for i in range(1, self.time_slices):
            sd += pendulum.duration(hours=self.slice_duration_hrs[i - 1])
            self.slice_start_utc[i] = sd
            self.slice_start_unix_seconds[i] = int(sd.timestamp())

    @property
    def year_start_utc(self) -> int:
        year_start_in_local_time = pendulum.datetime(
            self.flo_start_utc.year, 1, 1, 0, 0, 0, tz=self.timezone_string
        )
        utc_year_start = pendulum.datetime(self.flo_start_utc.year, 1, 1, 0, 0, 0)
        utc_delta_hrs = (
            year_start_in_local_time - utc_year_start
        ).total_seconds() / 3600
        year_start = utc_year_start + pendulum.duration(hours=utc_delta_hrs)
        return year_start
