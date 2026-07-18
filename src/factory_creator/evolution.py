from collections.abc import Callable

from .evolution_mutation import MoveBuildingMutation
from .fitness import Fitness
from .grid import Grid
from .hill_climbing import HillClimbing


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
