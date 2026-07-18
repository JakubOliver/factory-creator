import copy
from collections.abc import Callable, Iterator

from ..fitness import ConnectionPair
from .mutation import Mutation, MutationCandidate
from ...factory.factory import FactoryUtil
from ...graph_processing.graph_to_matrix import GraphToMatrix
from ...grid.grid import Grid
from ...grid.grid_entry import GridEntry, GridEntryTransportationId, GridEntryTypes


class MoveBuildingMutation(Mutation):
    """Moves each movable entry by one tile and reconnects its incident edges."""

    def __init__(
        self,
        show_failure_reasons: bool = True,
        start_generation: int = 0,
        end_generation: int | float = float("inf"),
    ) -> None:
        super().__init__(start_generation, end_generation)
        self.show_failure_reasons = show_failure_reasons

    @staticmethod
    def _get_changed_cords(cord: tuple) -> Iterator[tuple]:
        for dx, dy in Grid.GRID_MOVES:
            yield cord[0] + dx, cord[1] + dy

    def _generate(
        self,
        grid: Grid,
        report_method: Callable = print,
        error_report_method: Callable | None = None,
    ) -> Iterator[MutationCandidate]:
        factories = list(grid.get_factories())
        number_of_factories = len(factories)
        for processed, (active_cord, grid_entry) in enumerate(factories, start=1):
            yield from self._generate_for_building(
                grid,
                active_cord,
                grid_entry,
                report_method,
                error_report_method or report_method,
            )
            report_method(
                f"  Processed: {processed / number_of_factories * 100:.1f}% "
                f"({grid_entry.name})"
            )

    def _generate_for_building(
        self,
        grid: Grid,
        active_cord: tuple,
        grid_entry: GridEntry,
        report_method: Callable = print,
        error_report_method: Callable = print,
    ) -> Iterator[MutationCandidate]:
        for new_cord in self._get_changed_cords(active_cord):
            try:
                yield self._move_building(grid, active_cord, grid_entry, new_cord)
            except Exception as error:
                if self.show_failure_reasons:
                    error_report_method(f'  Individual failed because of "{error}"')

    @staticmethod
    def _move_building(
        grid: Grid,
        active_cord: tuple,
        grid_entry: GridEntry,
        new_cord: tuple,
    ) -> MutationCandidate:
        new_grid = copy.deepcopy(grid)
        neighbors = new_grid.erase_factory(active_cord)

        if grid_entry.entry_type == GridEntryTypes.Factory:
            new_grid.add_factory(
                new_cord,
                grid_entry.name,
                [cord for cord in FactoryUtil.get_cords(new_cord) if cord != new_cord],
            )
            active_cords = list(FactoryUtil.get_cords(new_cord))
            active_is_in_cords = FactoryUtil.get_cords_lambda(new_cord)
        else:
            new_grid.add_source(new_cord, grid_entry.name)
            active_cords = [new_cord]
            active_is_in_cords = lambda cord: cord == new_cord

        connection_pairs: list[ConnectionPair] = []
        for neighbor, direction in neighbors:
            neighbor_entry = new_grid.data[neighbor]
            if neighbor_entry.entry_type == GridEntryTypes.Factory:
                neighbor_cords = list(FactoryUtil.get_cords(neighbor))
                neighbor_is_in_cords = FactoryUtil.get_cords_lambda(neighbor)
            else:
                neighbor_cords = [neighbor]
                neighbor_is_in_cords = lambda cord, neighbor=neighbor: cord == neighbor

            if direction:
                start, start_cords, start_contains = (
                    new_cord,
                    active_cords,
                    active_is_in_cords,
                )
                end, end_cords, end_contains = (
                    neighbor,
                    neighbor_cords,
                    neighbor_is_in_cords,
                )
            else:
                start, start_cords, start_contains = (
                    neighbor,
                    neighbor_cords,
                    neighbor_is_in_cords,
                )
                end, end_cords, end_contains = (
                    new_cord,
                    active_cords,
                    active_is_in_cords,
                )

            GraphToMatrix.find_path(
                start,
                start_cords,
                start_contains,
                end,
                end_cords,
                end_contains,
                new_grid,
            )
            connection_pairs.append(
                (
                    start_cords,
                    end_cords,
                    GridEntryTransportationId.create_belt_id(
                        new_grid.data[start].get_id_text(),
                        new_grid.data[end].get_id_text(),
                    ),
                )
            )

        return MutationCandidate(new_grid, tuple(connection_pairs))
