from collections.abc import Callable, Iterator

from .mutation import Mutation, MutationCandidate
from ...graph_processing.graph_to_matrix import GraphToMatrix
from ...grid.grid import Grid
from ...grid.grid_entry import GridEntryTransportationId
from ...graph_processing import TopologicalSortGenerator
from ...util.cancellation import ComputationCancelled

#TODO: Now the disabling retry works, but it is possible, that for some recipes,
# the basic size is not enough and all orderings fails (for now this did not occured).
# But maybe add some check that if they all fail then we overwrite the retry option.
# So it starts using it. 

class MoveSubgraphMutation(Mutation):
    HOW_MANY_GENERATE_IN_ONE_GENERATION = 4

    def __init__(
        self,
        show_failure_reasons: bool = True,
        start_generation: int = 0,
        end_generation: int | float = float("inf"),
        retry_resizes: bool = True,
    ) -> None:
        super().__init__(start_generation, end_generation)
        self.show_failure_reasons = show_failure_reasons
        self.retry_resizes = retry_resizes

    def _generate(
        self,
        grid: Grid,
        report_method: Callable = print,
        error_report_method: Callable | None = None,
    ) -> Iterator[MutationCandidate]:
        graph = grid.get_connection_graph()

        for _ in range(self.HOW_MANY_GENERATE_IN_ONE_GENERATION):
            try:
                ordering = TopologicalSortGenerator.generate_random(graph)
                new_grid = GraphToMatrix.convert_via_heuristics(
                    graph,
                    report_method=report_method,
                    topological_ordering=ordering,
                    place_node_method=self._place_node,
                    stop_requested=self.stop_requested,
                    retry_resizes=self.retry_resizes,
                )
                yield MutationCandidate(
                    new_grid,
                    self._get_connection_pairs(graph, new_grid),
                    self.get_cache_key(ordering),
                )
            except ComputationCancelled:
                raise
            except Exception as error:
                if self.show_failure_reasons:
                    (error_report_method or report_method)(
                        f'  Individual failed because of "{error}"'
                    )

    def get_cache_key(self, ordering: list) -> int:
        if not isinstance(ordering, list):
            raise TypeError("Expected a list instance for caching.")

        return hash(tuple(ordering))

    @staticmethod
    def _place_node(graph, node, cord: tuple, grid: Grid) -> str:
        entry = graph.nodes[node]["entry"]
        if entry.is_source():
            grid.add_source(cord, entry.name)
        else:
            original_cord = graph.nodes[node]["original_cord"]
            surroundings = [
                (
                    cord[0] + occupied[0] - original_cord[0],
                    cord[1] + occupied[1] - original_cord[1],
                )
                for occupied in entry.surroundings
            ]
            grid.add_factory(cord, entry.name, surroundings)
        return entry.name

    @staticmethod
    def _get_connection_pairs(
        graph,
        grid: Grid,
    ) -> tuple:
        pairs = []
        for start, end in graph.edges:
            start_cord = graph.nodes[start]["cord"]
            end_cord = graph.nodes[end]["cord"]
            start_entry = grid[start_cord]
            end_entry = grid[end_cord]
            pairs.append(
                (
                    [start_cord, *start_entry.surroundings],
                    [end_cord, *end_entry.surroundings],
                    GridEntryTransportationId.create_belt_id(
                        start_entry.get_id_text(),
                        end_entry.get_id_text(),
                    ),
                )
            )
        return tuple(pairs)
