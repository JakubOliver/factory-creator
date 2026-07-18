from collections.abc import Callable

from .fitness import Fitness
from .hill_climbing import HillClimbing
from .move_building_mutation import MoveBuildingMutation
from ..grid.grid import Grid


class Evolution:
    """Entry point for factory layout evolution."""

    @staticmethod
    def evolve(
        grid: Grid,
        iteration: int | float = float("inf"),
        stagnation_break: int = 10,
        create_presentation: bool = False,
        report_method: Callable[[str], None] = print,
    ) -> Grid | list[Grid]:
        # TODO: Add optional per-run fitness caching to avoid evaluating the same layout repeatedly.
        algorithm = HillClimbing(
            mutations=[MoveBuildingMutation(show_failure_reasons=True)],
            fitness=Fitness(),
            generation_print=True,
        )
        return algorithm.evolve(
            grid,
            iteration=iteration,
            stagnation_break=stagnation_break,
            create_presentation=create_presentation,
            report_method=report_method,
        )
