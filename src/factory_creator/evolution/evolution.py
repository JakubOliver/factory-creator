from collections.abc import Callable

from .fitness import Fitness
from .hill_climbing import HillClimbing
from .mutations import *
from ..grid.grid import Grid
from ..util.output import OutputLevel, OutputReporter


class Evolution:
    """Entry point for factory layout evolution."""

    @staticmethod
    def evolve(
        grid: Grid,
        iteration: int | float = float("inf"),
        stagnation_break: int = 10,
        create_presentation: bool = False,
        report_method: Callable = print,
        output_level: OutputLevel = OutputLevel.MEDIUM,
    ) -> Grid | list[Grid]:
        # TODO: Add optional per-run fitness caching to avoid evaluating the same layout repeatedly.
        # TODO: As its is currently implemented, the computation can be parallelized by running multipler hill climbs or mayber better parts of hill climbs in different threads and then combining the results.
        reporter = OutputReporter(report_method, output_level)
        reporter.low("Evolution started.")
        algorithm = HillClimbing(
            mutations=[
                MoveBuildingMutation(
                    show_failure_reasons=True,
                    #start_generation=iteration // 5
                    start_generation= 10
                ),
                MoveSubgraphMutation(show_failure_reasons=True),
            ],
            fitness=Fitness(),
            generation_print=True,
        )
        return algorithm.evolve(
            grid,
            iteration=iteration,
            stagnation_break=stagnation_break,
            create_presentation=create_presentation,
            report_method=reporter.high,
            generation_report_method=reporter.low,
            error_report_method=reporter.medium,
        )
