import copy
import random
from collections.abc import Callable, Hashable, Iterator

from ..fitness_aspects import ConnectionPair
from .mutation import Mutation, MutationCandidate
from ...factory.factory import FactoryUtil
from ...graph_processing.graph_to_matrix import GraphToMatrix
from ...grid.grid import Grid
from ...grid.grid_entry import GridEntry, GridEntryTransportationId, GridEntryTypes
from ...util.cancellation import ComputationCancelled, raise_if_cancelled

BUILDINGS_PER_MUTATION = 4


class MoveBuildingMutation(Mutation):
    """Moves randomly selected entries by one tile and reconnects their edges."""

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

    @staticmethod
    def _get_attempt_key(
        source_state: int,
        active_cord: tuple,
        grid_entry: GridEntry,
        new_cord: tuple,
    ) -> tuple:
        return (
            source_state,
            grid_entry.get_id_text(),
            active_cord,
            new_cord,
        )

    def _has_untried_move(
        self,
        source_state: int,
        active_cord: tuple,
        grid_entry: GridEntry,
    ) -> bool:
        return any(
            not self._is_attempt_cached(
                self._get_attempt_key(
                    source_state,
                    active_cord,
                    grid_entry,
                    new_cord,
                )
            )
            for new_cord in self._get_changed_cords(active_cord)
        )

    def _generate(
        self,
        grid: Grid,
        report_method: Callable = print,
        error_report_method: Callable | None = None,
    ) -> Iterator[MutationCandidate]:
        source_state = grid.state_key_memory()
        factories = [
            (active_cord, grid_entry)
            for active_cord, grid_entry in grid.get_factories()
            if self._has_untried_move(
                source_state,
                active_cord,
                grid_entry,
            )
        ]
        selected_factories = random.sample(
            factories,
            k=min(BUILDINGS_PER_MUTATION, len(factories)),
        )
        number_of_selected_factories = len(selected_factories)

        for processed, (active_cord, grid_entry) in enumerate(
            selected_factories,
            start=1,
        ):
            yield from self._generate_for_building(
                grid,
                active_cord,
                grid_entry,
                report_method,
                error_report_method or report_method,
                source_state,
            )
            report_method(
                f"  Processed: {processed / number_of_selected_factories * 100:.1f}% "
                f"({grid_entry.name})"
            )

    def _generate_for_building(
        self,
        grid: Grid,
        active_cord: tuple,
        grid_entry: GridEntry,
        report_method: Callable = print,
        error_report_method: Callable = print,
        source_state: int | None = None,
    ) -> Iterator[MutationCandidate]:
        if source_state is None:
            source_state = grid.state_key_memory()

        for new_cord in self._get_changed_cords(active_cord):
            attempt_key = self._get_attempt_key(
                source_state,
                active_cord,
                grid_entry,
                new_cord,
            )
            if self._is_attempt_cached(attempt_key):
                continue

            try:
                yield self._move_building(
                    grid,
                    active_cord,
                    grid_entry,
                    new_cord,
                    attempt_key,
                )
            except ComputationCancelled:
                raise
            except Exception as error:
                if self.show_failure_reasons:
                    error_report_method(f'  Individual failed because of "{error}"')
                yield MutationCandidate(
                    grid=None,
                    attempt_key=attempt_key,
                )

    def _move_building(
        self,
        grid: Grid,
        active_cord: tuple,
        grid_entry: GridEntry,
        new_cord: tuple,
        attempt_key: Hashable | None = None,
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
            raise_if_cancelled(self.stop_requested)
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

        return MutationCandidate(
            grid=new_grid,
            connection_pairs=tuple(connection_pairs),
            attempt_key=attempt_key,
        )
